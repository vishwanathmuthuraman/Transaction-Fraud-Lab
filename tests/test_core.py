import copy
import json
from pathlib import Path

import pytest

from transaction_fraud_lab.common import ContractError
from transaction_fraud_lab.core import as_of_features, eligible_labels, inspect, review_queue

ROOT = Path(__file__).resolve().parents[1]
CASES = sorted((ROOT / "examples").glob("*.case.json"))


@pytest.fixture
def case():
    return json.loads((ROOT / "examples/ordinary-history.case.json").read_text())


@pytest.mark.parametrize("path", CASES, ids=lambda path: path.stem)
def test_development_eligibility_against_separate_expectations(path):
    case = json.loads(path.read_text())
    expected = json.loads(path.with_name(path.name.replace(".case.", ".expected.")).read_text())
    if expected["expected_status"] != "valid_input":
        with pytest.raises(ContractError):
            inspect(case)
    else:
        result = inspect(case)
        assert set(result["eligible_history_ids"]) == set(expected["eligible_history_ids"])
        labels = eligible_labels(case["labels"], case["organization_id"], case["training_cutoff"])
        assert {row["payment_id"] for row in labels} == set(expected["eligible_training_label_ids"])


def test_hand_checked_behavior_features(case):
    result = inspect(case)["features"]
    assert result == {
        "sender_count_24h": 1,
        "sender_amount_24h_minor": 1000,
        "sender_history_count": 1,
        "recipient_new_to_sender": False,
        "recipient_prior_sender_count": 1,
        "cold_start": False,
    }


def test_oracle_labels_cannot_change_features(case):
    original = inspect(case)
    case["labels"][0]["class"] = "fraudulent"
    assert inspect(case) == original


def test_current_payment_must_be_available(case):
    case["observations"][-1]["available_at"] = "2026-01-10T11:00:00Z"
    with pytest.raises(ContractError, match="unavailable"):
        inspect(case)


def test_float_money_rejected(case):
    case["observations"][0]["amount_minor"] = 1000.0
    with pytest.raises(ContractError):
        inspect(case)


def test_label_cutoffs_are_stage_specific(case):
    label = case["labels"][0]
    assert eligible_labels([label], case["organization_id"], "2026-01-10T08:59:59Z") == []
    assert eligible_labels([label], case["organization_id"], "2026-01-10T09:00:00Z") == [label]


def queue_rows(count):
    return [
        {
            "payment_id": "syn-pay-" + str(i),
            "organization_id": "syn-org-demo",
            "currency": "GBP",
            "day": "2026-01-10",
            "score": 1,
        }
        for i in range(count)
    ]


def test_small_cohort_does_not_round_up_review_budget():
    result = review_queue(queue_rows(9), "0.1")
    assert result["capacity"] == 0
    assert result["selected"] == []


def test_decimal_context_cannot_round_capacity_up():
    assert review_queue(queue_rows(1), "0.999999999999999999999999999999")["capacity"] == 0


def test_close_ranking_scores_keep_exact_order():
    rows = queue_rows(2)
    rows[0]["score"] = "0.100000000000000000000000000001"
    rows[1]["score"] = "0.100000000000000000000000000002"
    assert review_queue(rows, "0.5")["selected"][0]["payment_id"] == rows[1]["payment_id"]


def test_fixed_capacity_and_deterministic_ties():
    rows = queue_rows(20)
    assert review_queue(rows, "0.1")["capacity"] == 2
    assert review_queue(rows, "0.1") == review_queue(list(reversed(rows)), "0.1")


def test_review_does_not_accept_oracle_fields():
    rows = queue_rows(1)
    rows[0]["class"] = "fraudulent"
    with pytest.raises(ContractError):
        review_queue(rows, "1")


def test_multiple_daily_scopes_not_silently_pooled():
    rows = queue_rows(2)
    rows[0]["organization_id"] = "other"
    with pytest.raises(ContractError):
        review_queue(rows, "1")


@pytest.mark.parametrize("rate", ["NaN", "Infinity", "-0.1", "1.01"])
def test_invalid_review_fraction(rate):
    with pytest.raises(ContractError):
        review_queue(queue_rows(1), rate)


def test_feature_boundary_has_no_label_parameter(case):
    original = copy.deepcopy(case["observations"])
    as_of_features(
        case["observations"],
        case["organization_id"],
        case["current_payment_id"],
        case["scoring_at"],
    )
    assert case["observations"] == original
