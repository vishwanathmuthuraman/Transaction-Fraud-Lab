"""Label-free, organization-scoped payment features and bounded batch review."""

from datetime import timedelta
from decimal import Decimal, InvalidOperation

from .common import ContractError, digest, exact_integer, timestamp, validate_shape


def admit_payments(records, organization_id):
    admitted = {}
    currency = None
    for record in records:
        validate_shape(record, "payment")
        exact_integer(record["amount_minor"])
        occurred, available = timestamp(record["occurred_at"]), timestamp(record["available_at"])
        if occurred > available:
            raise ContractError("availability precedes occurrence")
        if record["organization_id"] != organization_id:
            raise ContractError("organization mismatch")
        if currency is not None and currency != record["currency"]:
            raise ContractError("mixed-currency experiment")
        currency = record["currency"]
        key = record["payment_id"]
        if key in admitted and admitted[key] != record:
            raise ContractError("conflicting payment identity")
        admitted[key] = record
    return admitted


def as_of_features(records, organization_id, payment_id, scoring_at):
    """No label argument exists at this scoring boundary."""
    admitted = admit_payments(records, organization_id)
    if payment_id not in admitted:
        raise ContractError("current payment is absent")
    current = admitted[payment_id]
    cutoff = timestamp(scoring_at)
    event_at = timestamp(current["occurred_at"])
    if timestamp(current["available_at"]) > cutoff:
        raise ContractError("current payment unavailable at scoring")
    history = [
        row
        for row in admitted.values()
        if timestamp(row["occurred_at"]) < event_at and timestamp(row["available_at"]) <= cutoff
    ]
    history.sort(key=lambda row: (timestamp(row["occurred_at"]), row["payment_id"]))
    sender_history = [row for row in history if row["sender_id"] == current["sender_id"]]
    day_history = [
        row
        for row in sender_history
        if timestamp(row["occurred_at"]) >= event_at - timedelta(days=1)
    ]
    total = exact_integer(sum(row["amount_minor"] for row in day_history))
    prior_payees = {row["recipient_id"] for row in sender_history}
    incoming_senders = {
        row["sender_id"] for row in history if row["recipient_id"] == current["recipient_id"]
    }
    return {
        "schema_version": "0.1",
        "kind": "as_of_feature_snapshot",
        "organization_id": organization_id,
        "payment_id": payment_id,
        "scoring_at": scoring_at,
        "currency": current["currency"],
        "eligible_history_ids": [row["payment_id"] for row in history],
        "features": {
            "sender_count_24h": len(day_history),
            "sender_amount_24h_minor": total,
            "sender_history_count": len(sender_history),
            "recipient_new_to_sender": current["recipient_id"] not in prior_payees,
            "recipient_prior_sender_count": len(incoming_senders),
            "cold_start": not sender_history,
        },
        "predictive_model_implemented": False,
    }


def eligible_labels(labels, organization_id, knowledge_cutoff):
    """Separate training/evaluation helper; never called by as_of_features."""
    cutoff = timestamp(knowledge_cutoff)
    seen = set()
    eligible = []
    for label in labels:
        validate_shape(label, "label")
        if label["organization_id"] != organization_id:
            raise ContractError("organization mismatch")
        key = label["payment_id"]
        if key in seen:
            raise ContractError("duplicate label identity")
        seen.add(key)
        if label["status"] == "resolved" and timestamp(label["available_at"]) <= cutoff:
            eligible.append(label)
    return sorted(eligible, key=lambda row: row["payment_id"])


def review_queue(rows, review_fraction):
    """One offline daily cohort; ranking score is not a probability."""
    try:
        fraction = Decimal(str(review_fraction))
    except InvalidOperation as exc:
        raise ContractError("invalid review fraction") from exc
    if not fraction.is_finite() or not 0 <= fraction <= 1:
        raise ContractError("review fraction must be between zero and one")
    keys, cohorts = set(), set()
    for row in rows:
        if set(row) != {"payment_id", "organization_id", "currency", "day", "score"}:
            raise ContractError("unexpected review-row fields")
        key = row["organization_id"], row["payment_id"]
        if key in keys:
            raise ContractError("duplicate queue identity")
        keys.add(key)
        cohorts.add((row["organization_id"], row["currency"], row["day"]))
        if isinstance(row["score"], bool):
            raise ContractError("invalid ranking score")
        try:
            score = Decimal(str(row["score"]))
        except InvalidOperation as exc:
            raise ContractError("invalid ranking score") from exc
        if not score.is_finite():
            raise ContractError("invalid ranking score")
    if len(cohorts) > 1:
        raise ContractError("review queue must contain one scoped daily cohort")
    numerator, denominator = fraction.as_integer_ratio()
    capacity = numerator * len(rows) // denominator
    ranked = sorted(
        rows,
        key=lambda row: (
            Decimal(str(row["score"])).copy_negate(),
            digest({"organization_id": row["organization_id"], "payment_id": row["payment_id"]}),
        ),
    )
    return {
        "capacity": capacity,
        "eligible_count": len(rows),
        "selected": ranked[:capacity],
        "mode": "offline_batch_review",
        "score_semantics": "ranking_signal_for_review",
    }


def inspect(case):
    validate_shape(case, "case")
    return as_of_features(
        case["observations"],
        case["organization_id"],
        case["current_payment_id"],
        case["scoring_at"],
    )
