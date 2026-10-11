# 02 — Architecture and language choices

## One auditable research process

Use a Python package with small pure-function modules and a CLI. Local JSONL is the canonical interchange; Parquet and DuckDB may be added for efficient feature tables after the JSON contract is fixed. Scikit-learn provides the initial baselines and calibration. NumPy supports seeded simulation, and pandas or Polars may be selected for table operations after measuring clarity and memory. Record a lockfile and exact versions at implementation time; no model dependencies are installed by this blueprint.

| Component | Responsibility | Planned location |
| --- | --- | --- |
| Contracts | Parse schemas and cross-record constraints | `src/transaction_fraud_lab/contracts.py` |
| Generator | Original synthetic timelines and separate labels | `simulation.py` |
| As-of store | Eligible historical observations by scope and timestamp | `history.py` |
| Feature engine | Behavioral aggregates and bounded graph features | `features/` |
| Splitter | Frozen chronological and entity-isolated partitions | `splits.py` |
| Training | Baselines, equal-budget tuning and model export | `training.py` |
| Scoring | Read-only features to typed risk signals | `scoring.py` |
| Policy | Bounded review queue and deterministic ties | `review_policy.py` |
| Evaluation | Mature labels and metrics, separate from scorer | `evaluation.py` |
| Reporting | Escaped static report and evidence JSON | `reporting.py` |

These files are planned, not implemented.

## Data flow and trust boundaries

A generator writes payments and oracle labels to different paths. The feature process receives payment history and the decision clock, never the oracle. The trainer, model selector, calibrator and policy selector each receive only their own partition and labels available by their separate knowledge cutoff. The staged maturity schedule in chapter 04 prevents a later-arriving label from changing an earlier decision. Freeze and hash all decision artifacts before the first final-test score. A scored manifest is frozen before the evaluator can read final labels. The evaluator may compute metrics but may not change predictions. Reports link to evidence by synthetic IDs and show input/data/model hashes.

For production-like replay use occurrence time for behavioral windows and availability time for knowledge. A history row is eligible only when its organization matches, `occurred_at < current.occurred_at`, and `available_at <= current.scoring_at`. Current transaction fields are allowed if `available_at <= scoring_at`. Equal occurrence-time batches use a shared pre-batch snapshot; no arbitrary file sort leaks one simultaneous row into another. Late historical corrections produce a new version and a new replay run, never silently rewrite prior score evidence.

## Model family strategy

Start with constant prevalence scoring, a seeded random ranking reference, explicit rules, L2 logistic regression and histogram gradient boosting. Report every baseline; tree depth and tuning attempts are capped before comparison. Candidate A adds as-of behavior features, candidate B adds as-of local graph aggregates, and candidate C optionally uses a declared anomaly channel. Never mix uncalibrated anomaly values with probabilities without a development-only policy and a disclosed meaning.

A GNN is a later experiment only if local graph features demonstrate useful incremental information and the graph protocol remains valid. Complex models must earn their maintenance cost. The first contribution can be a strong evaluation design and an informative failure analysis.

## Why Python, and when Rust or Go belongs

Python is the default because the scientific ecosystem supports reproducible statistics and model comparison. Rust is an optional adapter for an independently specified inference hot path after CPU, memory and latency profiles identify a need. Require a shared golden feature matrix, score tolerances and queue-order parity before adoption. Go is a reasonable future integration-service choice when team operations and concurrency favor it, but a second service is unnecessary for R1. Ruby on Rails can serve a later workflow product; it does not improve the research algorithm itself.

A language change requires a decision record naming measurable benefit, operational cost, owner, rollback and parity tests. Obscure code or language choice is not a defensible protection strategy. Public demonstration code can be inspected and copied; sensitive production tuning and data belong in a separate private system.

## Storage and model safety

Write immutable run folders with a UUID and hashes. Reject path traversal and refuse an existing output directory. Use JSON and standard tabular artifacts. Never load an untrusted Python pickle merely to inspect a model. Model bundles require provenance and a supported export format; if the chosen estimator cannot be safely exported, restrict its artifact to the trusted local experiment environment and explicitly document that limit.

No database, cloud queue, banking credential, hosted dashboard or external language-model service is necessary. The only currently working scripts validate documentation and synthetic fixture contracts.
