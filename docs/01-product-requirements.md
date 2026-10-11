# 01 — Product and research requirements

## User problem and bounded product

A payment-risk analyst must inspect a finite queue. A detector that ranks every unusual payment as suspicious can waste that queue and inconvenience legitimate people. The R1 product is an offline CLI and static evidence report for a researcher to compare ranking methods under identical synthetic conditions. It does not decide whether a payment is legal, recover money or infer intent.

The target is a **simulated fraudulent account-to-account payment**. Synthetic ground truth means the simulator's assigned event class, not a criminal finding. AML suspicion describes a different target and workflow; plausible laundering-like network motifs may inform a future study but must not be relabeled as payment fraud without a defined target and evidence. Company books and journal-entry anomalies belong in the separate financial-integrity project.

## Personas and exact journey

The research engineer selects a frozen experiment configuration. The data engineer generates synthetic events plus a physically separate oracle table, validates both, creates chronological partitions and materializes as-of features. The model developer trains only on eligible observations, chooses a model using development periods and freezes it. The independent reviewer runs the final evaluator, inspects all failures and signs the result card. A demo viewer sees a bounded ranked queue, evidence timestamps and the explicit phrase “risk signal for review.”

Success means a reproducible comparison that stands up to criticism about leakage, scarce labels, false positives and shifted behavior. Success does not require a neural network or a positive result.

## Releases

| Release | Deliverable | Exit gate |
| --- | --- | --- |
| R0 | This blueprint and reviewed synthetic specifications | Documentation validated; application remains pending |
| R1 | Offline synthetic generation, baselines, features, evaluation and report | All mandatory acceptance checks and independent reproduction |
| R2 | Optional research extension using authorized external dataset | Dataset license, relevance, target definition and privacy review complete |
| R3 | Optional private supervised institutional experiment | Separate agreement, security assessment, model governance and explicit authorization |

R2 and R3 are not included in the R1 completion claim. A future service may return risk scores; live blocking and regulatory reporting remain separate institutional responsibilities.

## Functional requirements

The [requirements register](../planning/requirements.csv) is the machine-readable source. Each requirement maps to an [acceptance-test specification](../planning/acceptance-tests.csv). These records describe proposed behavior; they are not implementation or execution evidence.

### FR01 — Input contracts

Validate versioned synthetic payment, label and experiment schemas before work; reject unexpected fields and malformed timestamps.

### FR02 — Identity and scope

Use organization plus synthetic identifier as every entity key; reject cross-organization scoring context.

### FR03 — Money

Store nonnegative integer minor units and currency; compare amounts within one currency, never implicit currency conversion.

### FR04 — Time availability

Features use only records available at scoring time and occurrences before the current event; equal-time cohorts cannot see each other.

### FR05 — Duplicate semantics

Same payment ID and identical payload is one event; same ID with a different payload is a contract error.

### FR06 — Delayed labels

Every supervised stage receives only resolved labels available by its own knowledge cutoff; training, selection, calibration and policy artifacts freeze before first final-test score.

### FR07 — Unknown outcomes

Unresolved and censored outcomes remain unknown; metrics disclose denominators and maturity coverage.

### FR08 — Synthetic generator

Generate legitimate and risky behavior from different probabilistic mechanisms with overlapping feature distributions, explicit seeds and original data.

### FR09 — Legitimate controls

Include payroll, high-value purchases, new customers, shared payees and travel-like behavior as legitimate hard negatives.

### FR10 — Temporal split

Freeze nonoverlapping chronological observation windows, maturity intervals, per-stage knowledge cutoffs, label coverage gates and all decision artifacts before final-test scoring.

### FR11 — Entity holdout

Report a separate cold-entity/component test with disjoint synthetic actor components and no train-test graph edges.

### FR12 — Preprocessing

Fit imputers, encoders, scalers, resampling and feature selection on eligible training only.

### FR13 — Behavior features

Compute rolling counts and amounts, payee novelty and changes relative to permitted prior history with cold-start indicators.

### FR14 — Graph features

Compute bounded local graph features from eligible historical edges; no future centrality or label-based graph contamination.

### FR15 — Baselines

Run prevalence/random ordering, declared rules, regularized logistic regression and a tabular tree baseline on identical rows.

### FR16 — Candidate ablation

Compare tabular features against behavioral and graph additions under equal tuning budgets.

### FR17 — Calibration

Fit calibration on exclusive chronological rows and labels available by its own cutoff; calibration artifact freezes before policy and final-test scoring.

### FR18 — Review capacity

Enforce a declared queue capacity and deterministic ties; operational top-K batch results are not called real-time blocking results.

### FR19 — Evidence output

Return model version, score type, timestamps, reason features, uncertainty and counterevidence with no allegation.

### FR20 — Metric completeness

Report precisely named resolved-subset metrics and population bounds, selected/unselected unknown counts, amount weighting and a paired component bootstrap that recomputes daily K and queues.

### FR21 — Cost model

Report a known-outcome cost subtotal plus lower/upper full-population bounds covering both selected and unselected unknown payments; distinguish modeled from realized savings.

### FR22 — Subgroup assessment

Report predeclared behavior and customer-age slices plus sample counts; suppress unsupported small-sample claims.

### FR23 — Drift

Evaluate covariate and typology shifts plus delayed-feedback windows without automatic retraining on test labels.

### FR24 — Reproducibility

Record code/data/split/feature/model hashes, environment, seeds, freeze cutoffs, configuration and failures.

### FR25 — Reviewer workflow

Present a ranked offline queue and traceable evidence; record review outcome independently from model score.

### FR26 — Secure boundaries

No network calls or live actions in R1; escape report content; deny untrusted executable model formats.

### FR27 — Performance measurements

Measure end-to-end latency, memory and throughput on disclosed hardware; optimization cannot silently change feature semantics.

### FR28 — Research claims

Record null results and limitations; no funding, novelty, award, certification or production-readiness claim without evidence.

### FR29 — Independent reproduction

Reproduce deterministic fixtures and aggregate experiment results in a second clean environment with documented tolerance.

### FR30 — Public release control

Publish only reviewed public artifacts and authorized sources; full sensitive methods, private data and operational thresholds stay outside a public export.

## Nonfunctional limits

R1 should run on a developer machine without a GPU. Start with 10,000 transactions for smoke evaluation and plan 250,000 for a controlled reference run; record actual counts rather than calling those counts completed. Keep 2 million events as an optional scale test. Memory and runtime limits must be fixed in preregistration before comparison. R1 is batch research; any “real-time” claim requires a distinct streaming policy and no future cohort ranking.

No demographic protected attribute is necessary to generate the base experiment. Synthetic behavioral slices are useful diagnostics but cannot establish real-world fairness. Any later demographic analysis requires appropriate lawful data access, domain review and sufficient samples.
