# Initial implementation — 0.1.0

This is the first implemented offline slice. “Complete” below means the bounded component passed the recorded checks; it does not mean the proposed product or evaluation is complete.

## Completed component tasks

| Task | Work | Status | Delivered behavior |
|---|---|---|---|
| C01 | Build the as-of payment feature boundary | Complete for this slice | Organization/currency admission, exact duplicate handling, strict amount types, occurrence/availability filtering, sender history and local incoming-sender features; no label argument. |
| C02 | Separate label eligibility and review capacity | Complete for this slice | Cutoff-bounded resolved-label helper, plus deterministic daily batch ranking with floor capacity, stable ties and explicit ranking-signal semantics. |
| C03 | Package, test and document the slice | Complete for this slice | Independent Python package, packaged existing schema resources, locked dependencies, CLI error behavior, behavioral tests, CI and captured demo evidence. |

Source: [core](../src/transaction_fraud_lab/core.py), [contracts/utilities](../src/transaction_fraud_lab/common.py), [CLI](../src/transaction_fraud_lab/cli.py), [behavioral tests](../tests/test_core.py), [CLI tests](../tests/test_cli.py). Runtime selection is recorded in [ADR 0001](decisions/0001-offline-core.md).

## What actually ran

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

## Relationship to the full plan

Contracts/eligibility and candidate feature/queue milestones have partial evidence. Generator, trained baselines, calibration, entity splits, evaluation metrics and frozen evaluation remain pending.

The [build plan](03-build-plan.md), [requirements](01-product-requirements.md), [evaluation](04-evaluation.md) and [definition of done](05-definition-of-done.md) remain the release criteria. Planned acceptance registers describe the wider system; partial progress does not replace their full conditions. Documentation checks validate authored artifacts separately from application CI.

## Explicit limits

There is no trained fraud detector, calibrated probability, original corpus generator, streaming/online queue or measured predictive result. The queue API accepts supplied ranking scores for one scoped offline daily cohort; it is not a deployed review policy. The CLI features command never calls the label helper.

All example records and observations are synthetic. No network integration or external business action exists in this slice. Financial and property results support human review. No customer impact, trained-model quality, production readiness or independent endorsement is established.

## Next implementation steps

1. Implement the original synthetic generator and chronological partitions with entity/lineage audits and legitimate hard negatives.
2. Add transparent rules and trained baselines with fit-time cutoffs, score types and calibration boundaries; validate metric arithmetic by hand.
3. Freeze model, policy, capacity and experiment hashes before final-test scoring, then publish all errors, null results and mature-label coverage.

For each step, add meaningful failure-case tests, capture actual output, preserve evidence/time/money boundaries, and update this record with the revision and unresolved limitations. Do not mark the full release complete from component test counts.
