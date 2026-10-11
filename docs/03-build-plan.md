# 03 — Research milestones

Initial offline components are implemented and verified. See [component progress and actual evidence](IMPLEMENTATION.md). Contracts/eligibility and candidate feature/queue milestones have partial evidence. Generator, trained baselines, calibration, entity splits, evaluation metrics and frozen evaluation remain pending. The milestones below retain their complete acceptance boundaries.

| Milestone | Public deliverable | Evidence required to advance | Current status |
| --- | --- | --- | --- |
| Contracts and eligibility | Versioned payment and label contracts, deterministic money and as-of history | Tests for malformed input, conflicting duplicates, scope isolation, unavailable labels and future observations | Planned |
| Synthetic study and baselines | Original generator, legitimate controls and transparent ranking baselines | Reviewed generator assumptions, chronological partitions and reproducible baseline runs | Planned |
| Candidate methods | Behavioral and bounded graph features with calibrated scores and a constrained queue | Equal-budget ablations, explicit score semantics and hand-checked metric behavior | Planned |
| Frozen evaluation | Preregistered temporal and cold-entity studies | Hashed artifacts, independent held-out cases, mature-label coverage and uncertainty estimates | Planned |
| Reproducible findings | Result card, minimal runnable demonstration and measured resource use | Traceable outputs, all failures and null findings, and reproduction in a second environment | Planned |

## Research discipline

Preserve the [requirements](../planning/requirements.csv) and [acceptance-test specifications](../planning/acceptance-tests.csv) as the public contracts. A planned acceptance test becomes evidence only after an implementation is run and its actual output is recorded.

The [evaluation protocol](04-evaluation.md) controls information availability, train/selection/calibration/policy boundaries, review capacity, population bounds and paired uncertainty estimates. Publish sufficient implementation and synthetic data to reproduce any claimed result. Never present expected fixture answers as model outputs.

Method complexity must be justified by experiments. Compare simple baselines before adding graph models, streaming infrastructure or another implementation language. A negative finding is a valid research outcome when the protocol and analysis are sound.

See the [definition of done](05-definition-of-done.md) for the distinction between documentation, engineering, research and production readiness.
