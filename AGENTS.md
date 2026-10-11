# Project working instructions

This folder contains a research and implementation blueprint, not a trained fraud detector. Read README.md and docs/01-product-requirements.md through docs/05-definition-of-done.md before implementing. Only the commands in README.md and docs/IMPLEMENTATION.md are implemented interfaces; other product/training commands remain future targets.

## Research and implementation discipline

1. Follow the public milestones in docs/03-build-plan.md. Detailed internal task schedules are maintained separately. Preserve requirement IDs and acceptance mappings; record real evidence before describing work as complete.
2. Use Python for research, simulation, feature extraction, training and evaluation. Use integer minor units for money. A Rust inference adapter is optional after profiling demonstrates a bottleneck; use an architecture decision and parity benchmark. Choose languages for ecosystem, safety, latency, operations and team maintainability, never prestige.
3. Preserve occurrence time, availability time, decision time and label availability separately. A feature may use only evidence available at the decision. Keep oracle labels outside scoring processes. Enforce separate knowledge cutoffs for training, model selection, calibration and policy decisions; freeze every decision artifact before final-test scoring. Unknown labels are not legitimate examples.
4. Use time-based development and held-out evaluation, with separate cold-entity isolation experiments. Do not fit preprocessing on validation or test sets, tune on held-out results, rebalance evaluation prevalence or select the best seed after seeing outcomes.
5. Output review-priority signals, evidence and uncertainty. Never claim a person committed fraud. Do not block payments, report people or connect to live financial systems in this project.
6. Keep all fixtures original and synthetic. No customer data, private affiliations, credentials, private commercial strategy or operational detection thresholds in a future public export.
7. A valid negative result is publishable. No invented benchmark scores, external endorsements, awards, certifications or completed-work claims.
8. Keep commits under the repository owner's explicitly configured identity. Do not add automated coauthor trailers or promotional tooling signatures. Preserve truthful contribution records and mandatory third-party notices.
9. This is the authorized curated public research edition. Do not add internal delivery schedules, commercial plans or private records. Future live integrations or unrelated publication require their own concrete scope.
10. Markdown is the source of truth; run scripts/check_public_docs.py and scripts/validate_blueprint.py after changes. Documentation validation is separate from application testing.

Read [ENGINEERING.md](ENGINEERING.md) for the persistent language, personal identity and publication rules.
