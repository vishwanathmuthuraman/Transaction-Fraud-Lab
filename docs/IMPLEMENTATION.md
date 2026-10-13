# Initial implementation — 0.1.0

This is the first implemented offline slice. “Complete” below means the bounded component passed the recorded checks; it does not mean the proposed product or evaluation is complete.

## Completed component tasks

| Task | Work | Status | Delivered behavior |
|---|---|---|---|
| C01 | Build the as-of payment feature boundary | Complete for this slice | Organization/currency admission, exact duplicate handling, strict amount types, occurrence/availability filtering, sender history and local incoming-sender features; no label argument. |
| C02 | Separate label eligibility and review capacity | Complete for this slice | Cutoff-bounded resolved-label helper, plus deterministic daily batch ranking with floor capacity, stable ties and explicit ranking-signal semantics. |
| C03 | Package, test and document the slice | Complete for this slice | Independent Python package, packaged existing schema resources, locked dependencies, CLI error behavior, behavioral tests, CI and captured demo evidence. |

Source: [core](../src/transaction_fraud_lab/core.py), [contracts/utilities](../src/transaction_fraud_lab/common.py), [CLI](../src/transaction_fraud_lab/cli.py), [behavioral tests](../tests/test_core.py), [CLI tests](../tests/test_cli.py). Runtime selection is recorded in [ADR 0001](decisions/0001-offline-core.md).

## Initial verification (historical)

Verified on Python **3.12.13**, Darwin: **36 tests passed, zero failed**, Ruff lint/format checks passed. A wheel was built, installed with locked dependency hashes into a fresh environment and exercised from outside the checkout; its schema files loaded from the installed package. The CLI input/output hashes and implementation-file hashes are in the [verification record](../reports/initial-implementation/verification.json). That file identifies exact tested inputs; expected specifications were not copied into an execution report.

```sh
uv sync --locked
uv run --locked fraud-lab features examples/ordinary-history.case.json
uv run --locked ruff check src tests
uv run --locked ruff format --check src tests
uv run --locked pytest
```

Observed demo: The ordinary-history command emits the eligible prior payment IDs and hand-checkable counts, sums, payee novelty and cold-start status. It emits no prediction or fraud conclusion. Tests separately exercise delayed labels, future edges, equal-time records and review capacity.

[Captured output](../reports/initial-implementation/demo-1.json). Test use of authored expected files is restricted to development assertions; application code does not open them. These are component regressions, not independent held-out evaluation or performance measurements.

## Synthetic generator and chronological partitions (step 1, partial)

Module [synthetic](../src/transaction_fraud_lab/synthetic.py), tests in [test_synthetic](../tests/test_synthetic.py). Implemented: a seeded (`random.Random`) generator of original synthetic payments in integer minor units, returned as three separate tables (payments with no class field, oracle labels with delayed availability and unresolved outcomes, and a pattern audit); legitimate hard negatives (new customers, payroll fan-out, high-value purchases) alongside an authored burst pattern; `partition_chronological` by occurrence time with strictly increasing, start-inclusive boundaries; `audit_partitions`, which reports cold senders per partition and, at each partition end, labels known, unresolved and not yet available, and rejects empty partitions, duplicate or missing label records and labels available before occurrence.

Commands run: `uv run --locked ruff format --check src tests`, `ruff check src tests`, `pytest` and both documentation scripts. Observed: 43 tests passed (7 new), lint and format passed, documentation checks passed.

### Partition audit review — 13 October 2026

Eight additional regressions failed on the initial draft: a test row moved into training, reversed audit boundaries, an extra partition, a foreign-organization label, a test label dated before its payment, invalid payment availability, an unmatched label and mixed-organization input. The audit now validates actual membership against the shared chronological splitter, reuses payment admission for scope/currency/money/time checks, requires exact label coverage and verifies label scope and timing across all three partitions. The availability summary has cutoffs for training and validation only; no final-test maturity cutoff or supervised-stage freeze is implied.

After repair, **51 source tests pass** (the original 43 plus 8 regression cases). These are component checks on synthetic data, not a fraud benchmark. No test labels are passed to the feature boundary.

Remaining limits: the generator patterns are authored assumptions, not reviewed against real data, and the fraud-like burst pattern is a toy. No generator CLI command, cold-entity split experiment, baseline or metric exists. Nothing here shows that results on synthetic data generalize to real fraud. The full staged maturity schedule remains future work.

## Relationship to the full plan

Contracts/eligibility, the seeded generator, chronological audit and candidate feature/queue milestones have partial evidence. Trained baselines, calibration, entity-isolated splits, evaluation metrics and frozen evaluation remain pending.

The [build plan](03-build-plan.md), [requirements](01-product-requirements.md), [evaluation](04-evaluation.md) and [definition of done](05-definition-of-done.md) remain the release criteria. Planned acceptance registers describe the wider system; partial progress does not replace their full conditions. Documentation checks validate authored artifacts separately from application CI.

## Explicit limits

There is no trained fraud detector, calibrated probability, validated study corpus, streaming/online queue or measured predictive result. The queue API accepts supplied ranking scores for one scoped offline daily cohort; it is not a deployed review policy. The CLI features command never calls the label helper.

All example records and observations are synthetic. No network integration or external business action exists in this slice. Financial and property results support human review. No customer impact, trained-model quality, production readiness or independent endorsement is established.

## Next implementation steps

1. Extend the seeded generator and chronological audit to the full maturity schedule and a separate entity-isolated study, with reviewed hard-negative assumptions.
2. Add transparent rules and trained baselines with fit-time cutoffs, score types and calibration boundaries; validate metric arithmetic by hand.
3. Freeze model, policy, capacity and experiment hashes before final-test scoring, then publish all errors, null results and mature-label coverage.

For each step, add meaningful failure-case tests, capture actual output, preserve evidence/time/money boundaries, and update this record with the revision and unresolved limitations. Do not mark the full release complete from component test counts.
