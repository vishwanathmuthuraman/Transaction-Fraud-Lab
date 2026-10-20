import copy

import pytest

from transaction_fraud_lab.common import ContractError, digest, timestamp
from transaction_fraud_lab.core import eligible_labels
from transaction_fraud_lab.synthetic import (
    audit_partitions,
    generate,
    partition_chronological,
    sender_lineage,
)

VALIDATION = "2026-01-25T00:00:00Z"
TEST = "2026-02-10T00:00:00Z"


@pytest.fixture(scope="module")
def data():
    return generate(7)


def test_same_seed_is_identical_and_different_seed_differs(data):
    assert digest(generate(7)) == digest(data)
    assert digest(generate(8)) != digest(data)


def test_payments_carry_no_oracle_fields(data):
    assert all(
        set(row)
        == {
            "payment_id",
            "organization_id",
            "sender_id",
            "recipient_id",
            "occurred_at",
            "available_at",
            "amount_minor",
            "currency",
            "channel",
            "device_id",
        }
        for row in data["payments"]
    )
    assert {row["payment_id"] for row in data["payments"]} == {
        row["payment_id"] for row in data["labels"]
    }


def test_hard_negatives_exist_and_are_legitimate(data):
    patterns = {row["pattern"] for row in data["audit"]}
    assert {"payroll", "high_value", "new_customer", "burst"} <= patterns
    labels = {row["payment_id"]: row for row in data["labels"]}
    for row in data["audit"]:
        if row["pattern"] in {"payroll", "high_value", "new_customer", "ordinary"}:
            assert row["legitimate"]
            assert labels[row["payment_id"]]["class"] in {"legitimate", None}


def test_label_availability_follows_occurrence_and_some_unresolved(data):
    statuses = {row["status"] for row in data["labels"]}
    assert statuses == {"resolved", "unresolved"}
    payments = {row["payment_id"]: row for row in data["payments"]}
    for label in data["labels"]:
        if label["status"] == "resolved":
            assert timestamp(label["available_at"]) > timestamp(
                payments[label["payment_id"]]["occurred_at"]
            )


def test_partitions_are_chronological_and_boundary_inclusive(data):
    parts = partition_chronological(data["payments"], VALIDATION, TEST)
    assert sum(map(len, parts.values())) == len(data["payments"])
    assert all(timestamp(r["occurred_at"]) < timestamp(VALIDATION) for r in parts["train"])
    assert all(
        timestamp(VALIDATION) <= timestamp(r["occurred_at"]) < timestamp(TEST)
        for r in parts["validation"]
    )
    assert all(timestamp(r["occurred_at"]) >= timestamp(TEST) for r in parts["test"])
    edge = copy.deepcopy(data["payments"][0])
    edge["payment_id"] = "syn-pay-edge"
    edge["occurred_at"] = edge["available_at"] = VALIDATION
    assert edge in partition_chronological([edge], VALIDATION, TEST)["validation"]


def test_audit_reports_cold_senders_and_late_labels(data):
    parts = partition_chronological(data["payments"], VALIDATION, TEST)
    report = audit_partitions(parts, data["labels"], VALIDATION, TEST)
    assert report["cold_senders"]["validation"] > 0
    train = report["labels_known_at_partition_end"]["train"]
    assert train["unresolved"] > 0 and train["not_yet_available"] > 0
    known = eligible_labels(data["labels"], "syn-org-generated", VALIDATION)
    assert train["known"] <= len(known)


def test_failures(data):
    with pytest.raises(ContractError):
        partition_chronological(data["payments"], TEST, VALIDATION)
    with pytest.raises(ContractError):
        partition_chronological(data["payments"], VALIDATION, VALIDATION)
    with pytest.raises(ContractError):
        partition_chronological(data["payments"] + data["payments"][:1], VALIDATION, TEST)
    with pytest.raises(ContractError):
        partition_chronological(data["payments"], "2026-01-25", TEST)
    parts = partition_chronological(data["payments"], VALIDATION, TEST)
    with pytest.raises(ContractError):
        audit_partitions(parts, data["labels"][:-1], VALIDATION, TEST)
    with pytest.raises(ContractError):
        audit_partitions({**parts, "test": []}, data["labels"], VALIDATION, TEST)
    with pytest.raises(ContractError):
        generate(-1)
    with pytest.raises(ContractError):
        generate(True)
    with pytest.raises(ContractError):
        generate(1, days=5)
    with pytest.raises(ContractError):
        generate(1, organization_id="real-org")


@pytest.mark.parametrize(
    "fault",
    [
        "wrong_window",
        "reversed_boundaries",
        "extra_partition",
        "foreign_label",
        "early_test_label",
        "invalid_payment",
        "unmatched_label",
    ],
)
def test_audit_rejects_invalid_partition_evidence(data, fault):
    parts = copy.deepcopy(partition_chronological(data["payments"], VALIDATION, TEST))
    labels = copy.deepcopy(data["labels"])
    validation, test = VALIDATION, TEST
    if fault == "wrong_window":
        parts["train"].append(parts["test"].pop())
    elif fault == "reversed_boundaries":
        validation, test = TEST, VALIDATION
    elif fault == "extra_partition":
        parts["unreviewed"] = parts["test"][:1]
    elif fault == "foreign_label":
        labels[0]["organization_id"] = "syn-org-foreign"
    elif fault == "early_test_label":
        target = parts["test"][0]["payment_id"]
        label = next(row for row in labels if row["payment_id"] == target)
        label.update(status="resolved", **{"class": "legitimate", "available_at": VALIDATION})
    elif fault == "invalid_payment":
        parts["train"][0]["available_at"] = "2025-01-01T00:00:00Z"
    elif fault == "unmatched_label":
        labels.append({**labels[0], "payment_id": "syn-pay-absent"})
    with pytest.raises(ContractError):
        audit_partitions(parts, labels, validation, test)


def test_partitioner_rejects_mixed_organizations(data):
    payments = copy.deepcopy(data["payments"])
    payments[-1]["organization_id"] = "syn-org-foreign"
    with pytest.raises(ContractError):
        partition_chronological(payments, VALIDATION, TEST)


def _pay(pid, sender, when):
    return {
        "payment_id": f"syn-pay-{pid}",
        "organization_id": "syn-org-a",
        "sender_id": sender,
        "recipient_id": "syn-account-r0001",
        "occurred_at": when,
        "available_at": when,
        "amount_minor": 1000,
        "currency": "GBP",
        "channel": "account_transfer",
        "device_id": None,
    }


def test_sender_lineage_matches_cold_sender_audit(data):
    parts = partition_chronological(data["payments"], VALIDATION, TEST)
    lineage = sender_lineage(parts, VALIDATION, TEST)
    report = audit_partitions(parts, data["labels"], VALIDATION, TEST)
    firsts = [entry["first_partition"] for entry in lineage.values()]
    assert firsts.count("validation") == report["cold_senders"]["validation"]
    assert firsts.count("test") == report["cold_senders"]["test"]
    assert sum(sum(e["payments"].values()) for e in lineage.values()) == len(data["payments"])


def test_sender_lineage_boundary_and_first_occurrence():
    rows = [
        _pay("p3", "syn-account-s2", TEST),
        _pay("p2", "syn-account-s1", VALIDATION),
        _pay("p1", "syn-account-s1", "2026-01-01T00:00:00Z"),
        _pay("p4", "syn-account-s3", "2026-01-02T00:00:00Z"),
    ]
    lineage = sender_lineage(partition_chronological(rows, VALIDATION, TEST), VALIDATION, TEST)
    assert lineage["syn-account-s1"]["first_partition"] == "train"
    assert lineage["syn-account-s1"]["payments"] == {"train": 1, "validation": 1, "test": 0}
    assert lineage["syn-account-s2"]["first_partition"] == "test"
    assert lineage["syn-account-s2"]["first_occurred_at"] == TEST


def test_sender_lineage_rejects_bad_membership():
    rows = [
        _pay("p1", "syn-account-s1", "2026-01-01T00:00:00Z"),
        _pay("p2", "syn-account-s2", TEST),
    ]
    parts = partition_chronological(rows, VALIDATION, TEST)
    parts["train"].append(parts["test"].pop())
    with pytest.raises(ContractError):
        sender_lineage(parts, VALIDATION, TEST)
    with pytest.raises(ContractError):
        sender_lineage({"train": []}, VALIDATION, TEST)
    with pytest.raises(ContractError):
        sender_lineage(partition_chronological(rows, VALIDATION, TEST), TEST, VALIDATION)
