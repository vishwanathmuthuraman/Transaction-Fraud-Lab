"""Original deterministic synthetic payments, separate oracle labels and chronological partitions."""

import random
from datetime import datetime, timedelta, timezone

from .common import ContractError, exact_integer, timestamp, validate_shape
from .core import admit_payments

ORIGIN = datetime(2026, 1, 1, tzinfo=timezone.utc)
PARTITIONS = ("train", "validation", "test")


def _iso(value):
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate(seed, organization_id="syn-org-generated", sender_count=40, days=60):
    """Return payments, oracle labels and a generator audit as three separate tables.

    Payments never carry a class or pattern. Labels and the pattern audit are for
    development/evaluation code only. Hard negatives are legitimate by construction.
    """
    exact_integer(seed, minimum=0)
    exact_integer(sender_count, minimum=1, maximum=2000)
    exact_integer(days, minimum=14, maximum=365)
    if not isinstance(organization_id, str) or not organization_id.startswith("syn-org-"):
        raise ContractError("organization must be synthetic")
    rng = random.Random(seed)
    recipients = [f"syn-account-r{k:04d}" for k in range(max(8, sender_count // 2))]
    drafts = []

    def add(sender, recipient, when, amount, pattern, fraud=False):
        drafts.append((when, sender, recipient, amount, pattern, fraud))

    for i in range(sender_count):
        sender = f"syn-account-s{i:04d}"
        start = rng.randrange(0, days - 10)
        favourites = rng.sample(recipients, 3)
        for day in range(start, days):
            if rng.randrange(3) == 0:
                when = ORIGIN + timedelta(days=day, seconds=rng.randrange(86400))
                add(sender, rng.choice(favourites), when, rng.randrange(500, 20001), "ordinary")
        if start > 0:
            when = ORIGIN + timedelta(days=start, seconds=rng.randrange(86400))
            add(sender, rng.choice(recipients), when, rng.randrange(20000, 60001), "new_customer")
        if i % 5 == 0:
            salary = rng.randrange(150000, 300001)
            for day in range(start + 3, days, 7):
                base = ORIGIN + timedelta(days=day, hours=9)
                for staff in rng.sample(recipients, 3):
                    add(
                        sender,
                        staff,
                        base + timedelta(seconds=rng.randrange(600)),
                        salary,
                        "payroll",
                    )
        if i % 7 == 1:
            when = ORIGIN + timedelta(days=rng.randrange(start, days), seconds=rng.randrange(86400))
            add(sender, rng.choice(recipients), when, rng.randrange(500000, 900001), "high_value")
        if i % 11 == 2:
            base = ORIGIN + timedelta(days=rng.randrange(start, days), seconds=rng.randrange(80000))
            for k, target in enumerate(rng.sample(recipients, 3)):
                amount = rng.randrange(80000, 200001)
                add(sender, target, base + timedelta(minutes=2 * k), amount, "burst", True)

    drafts.sort(key=lambda row: (row[0], row[1], row[2], row[3], row[4]))
    payments, labels, audit = [], [], []
    for n, (when, sender, recipient, amount, pattern, fraud) in enumerate(drafts):
        payment_id = f"syn-pay-{n:06d}"
        available = when + timedelta(seconds=rng.randrange(0, 301))
        payments.append(
            {
                "payment_id": payment_id,
                "organization_id": organization_id,
                "sender_id": sender,
                "recipient_id": recipient,
                "occurred_at": _iso(when),
                "available_at": _iso(available),
                "amount_minor": amount,
                "currency": "GBP",
                "channel": "account_transfer",
                "device_id": None,
            }
        )
        resolved = rng.randrange(10) != 0
        delay = timedelta(hours=rng.randrange(48, 481) if fraud else rng.randrange(24, 241))
        labels.append(
            {
                "payment_id": payment_id,
                "organization_id": organization_id,
                "status": "resolved" if resolved else "unresolved",
                "class": ("fraudulent" if fraud else "legitimate") if resolved else None,
                "available_at": _iso(when + delay) if resolved else None,
                "provenance": "original_synthetic_oracle",
            }
        )
        audit.append({"payment_id": payment_id, "pattern": pattern, "legitimate": not fraud})
    for row in payments:
        validate_shape(row, "payment")
    for row in labels:
        validate_shape(row, "label")
    return {"seed": seed, "payments": payments, "labels": labels, "audit": audit}


def partition_chronological(payments, validation_start, test_start):
    """Split by occurrence time: train < validation_start <= validation < test_start <= test."""
    first, second = timestamp(validation_start), timestamp(test_start)
    if first >= second:
        raise ContractError("partition boundaries must be strictly increasing")
    result = {name: [] for name in PARTITIONS}
    payments = list(payments)
    if payments:
        validate_shape(payments[0], "payment")
        # Reuse scoring admission: one organization/currency, valid money and times.
        admitted = admit_payments(payments, payments[0]["organization_id"])
        if len(admitted) != len(payments):
            raise ContractError("duplicate payment identity")
    seen = set()
    for row in payments:
        validate_shape(row, "payment")
        if row["payment_id"] in seen:
            raise ContractError("duplicate payment identity")
        seen.add(row["payment_id"])
        when = timestamp(row["occurred_at"])
        name = "train" if when < first else "validation" if when < second else "test"
        result[name].append(row)
    return result


def audit_partitions(partitions, labels, validation_start, test_start):
    """Validate chronological membership and report cold senders and label availability.

    Raises when a partition is empty. Label availability is reported against the
    boundary that ends the preceding partition, so unresolved or late labels are
    counted rather than treated as known.
    """
    if set(partitions) != set(PARTITIONS):
        raise ContractError("exactly train, validation and test partitions are required")
    if any(not partitions.get(name) for name in PARTITIONS):
        raise ContractError("every chronological partition must be non-empty")
    rows = [row for name in PARTITIONS for row in partitions[name]]
    expected = partition_chronological(rows, validation_start, test_start)
    for name in PARTITIONS:
        if {row["payment_id"] for row in partitions[name]} != {
            row["payment_id"] for row in expected[name]
        }:
            raise ContractError("payment outside declared chronological partition")
    by_id = {row["payment_id"]: row for row in rows}
    cutoffs = {"train": timestamp(validation_start), "validation": timestamp(test_start)}
    label_by_id = {}
    for label in labels:
        validate_shape(label, "label")
        if label["payment_id"] in label_by_id:
            raise ContractError("duplicate label identity")
        payment = by_id.get(label["payment_id"])
        if payment is None:
            raise ContractError("label has no payment record")
        if label["organization_id"] != payment["organization_id"]:
            raise ContractError("label organization mismatch")
        if label["status"] == "resolved" and timestamp(label["available_at"]) < timestamp(
            payment["occurred_at"]
        ):
            raise ContractError("label available before occurrence")
        label_by_id[label["payment_id"]] = label
    if set(by_id) - set(label_by_id):
        raise ContractError("payment has no label record")
    senders = {name: {row["sender_id"] for row in partitions[name]} for name in PARTITIONS}
    report = {
        "cold_senders": {
            "validation": len(senders["validation"] - senders["train"]),
            "test": len(senders["test"] - senders["train"] - senders["validation"]),
        },
        "labels_known_at_partition_end": {},
    }
    for name, cutoff in cutoffs.items():
        known = unresolved = late = 0
        for row in partitions[name]:
            label = label_by_id[row["payment_id"]]
            if label["status"] == "unresolved":
                unresolved += 1
            elif timestamp(label["available_at"]) <= cutoff:
                known += 1
            else:
                late += 1
        report["labels_known_at_partition_end"][name] = {
            "known": known,
            "unresolved": unresolved,
            "not_yet_available": late,
        }
    return report


def sender_lineage(partitions, validation_start, test_start):
    """Return each sender's first partition, first occurrence and per-partition payment counts.

    Membership is validated against the shared chronological splitter first.
    Lineage uses occurrence time only and never reads labels.
    """
    if set(partitions) != set(PARTITIONS):
        raise ContractError("exactly train, validation and test partitions are required")
    rows = [row for name in PARTITIONS for row in partitions[name]]
    expected = partition_chronological(rows, validation_start, test_start)
    for name in PARTITIONS:
        if {row["payment_id"] for row in partitions[name]} != {
            row["payment_id"] for row in expected[name]
        }:
            raise ContractError("payment outside declared chronological partition")
    lineage = {}
    for name in PARTITIONS:
        for row in partitions[name]:
            entry = lineage.setdefault(
                row["sender_id"],
                {
                    "first_partition": name,
                    "first_occurred_at": row["occurred_at"],
                    "payments": {part: 0 for part in PARTITIONS},
                },
            )
            entry["payments"][name] += 1
            if timestamp(row["occurred_at"]) < timestamp(entry["first_occurred_at"]):
                entry["first_occurred_at"] = row["occurred_at"]
    return dict(sorted(lineage.items()))
