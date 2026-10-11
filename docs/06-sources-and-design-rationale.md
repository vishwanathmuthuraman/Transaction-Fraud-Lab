# 06 — Sources and design rationale

Sources were reviewed on 11 October 2026. Institutional reports identify important problems; they do not prove an unserved market or validate this algorithm. The choices below are our proposed design responses. No report text, dataset or proprietary thresholds have been copied into the project. Dates marked undated indicate no publication date was established from the reviewed page.

## S01 — Cyber-enabled fraud: digitalisation and ML/TF/PF risks

**Publisher:** FATF. **Publication:** 2026-02-24. [Primary source](https://www.fatf-gafi.org/en/publications/Methodsandtrends/cyber-enabled-fraud-digitalisation-ml-tf-pf-risks.html).

Supported observation: Fraud and movement of proceeds are related but require different analytical and institutional responses.

Proposed design response: Separate payment-fraud target from AML suspicion; no automated allegations.

## S02 — Project Hertha

**Publisher:** BIS Innovation Hub. **Publication:** 2025-06-05. [Primary source](https://www.bis.org/project/hertha).

Supported observation: Payment-network analytics were studied using a synthetic payment ecosystem and have practical limitations.

Proposed design response: Compare local graph information as an experiment; synthetic success is not production evidence.

## S03 — Project Hertha report

**Publisher:** BIS Innovation Hub. **Publication:** 2025-06-05. [Primary source](https://www.bis.org/publ/othp96.pdf).

Supported observation: Research compares detection under a fixed target rate and examines known versus unseen patterns.

Proposed design response: Use fixed review capacity and held-out behavior experiments, with independent model baselines.

## S04 — Enhancing cross-border payments: addressing fraud

**Publisher:** BIS / PIE task force contributors. **Publication:** 2026-02. [Primary source](https://www.bis.org/cpmi/pietf/fraud_report_2026.pdf).

Supported observation: Report discusses fraud prevention initiatives and information sharing; contributor views are not blanket BIS endorsement.

Proposed design response: Treat network access and collaboration as separate constraints rather than assuming full visibility.

## S05 — Finding a needle in a haystack

**Publisher:** BIS working-paper authors. **Publication:** 2024-05-15. [Primary source](https://www.bis.org/publications/working-paper-1188-finding-needle-haystack-machine-learning-framework-anomaly-detection-payment-systems).

Supported observation: High-value payment anomaly research distinguishes typical payments from unusual transactions.

Proposed design response: Anomaly scores are useful baselines, but unusual is not a confirmed fraud label.

## S06 — Validation strategies

**Publisher:** Fraud Detection Handbook authors. **Publication:** undated; accessed 2026-10-11. [Primary source](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_5_ModelValidationAndSelection/ValidationStrategies.html).

Supported observation: Forward evaluation incorporates feedback delay and nonstationary behavior.

Proposed design response: Use chronological splits and as-of label eligibility.

## S07 — Baseline fraud detection system

**Publisher:** Fraud Detection Handbook authors. **Publication:** undated; accessed 2026-10-11. [Primary source](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_3_GettingStarted/BaselineModeling.html).

Supported observation: Real label discovery delays vary; a fixed delay is a simplification.

Proposed design response: Model a distribution of delays and explicit unresolved outcomes.

## S08 — Turning the Tables: Biased, Imbalanced, Dynamic Tabular Datasets

**Publisher:** Jesus et al. / NeurIPS. **Publication:** 2022. [Primary source](https://proceedings.neurips.cc/paper_files/paper/2022/hash/d9696563856bd350e4e7ac5e5812f23c-Abstract-Datasets_and_Benchmarks.html).

Supported observation: BAF is an account-opening fraud dataset suite designed for temporal dynamics, imbalance and bias evaluation.

Proposed design response: Optional distinct target extension; never claim payment-fraud validation from BAF alone.

## S09 — Bank Account Fraud dataset repository

**Publisher:** Feedzai. **Publication:** undated; accessed 2026-10-11. [Primary source](https://github.com/Feedzai/bank-account-fraud).

Supported observation: Official supporting repository describes access and usage context for BAF.

Proposed design response: Check actual data license and provenance before a future download; do not redistribute now.

## S10 — Common pitfalls and recommended practices

**Publisher:** scikit-learn maintainers. **Publication:** undated; accessed 2026-10-11. [Primary source](https://scikit-learn.org/stable/common_pitfalls.html).

Supported observation: Fitting transformations on held-out data leaks information into evaluation.

Proposed design response: Use train-only pipeline fitting and explicit leakage regression tests.

## S11 — average_precision_score reference

**Publisher:** scikit-learn maintainers. **Publication:** undated; accessed 2026-10-11. [Primary source](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html).

Supported observation: Average precision is a defined noninterpolated summary of precision-recall performance.

Proposed design response: Name AP precisely and distinguish trapezoidal PR area.

## S12 — Machine learning in UK financial services

**Publisher:** Bank of England and FCA. **Publication:** 2022-10-11. [Primary source](https://www.bankofengland.co.uk/report/2022/machine-learning-in-uk-financial-services).

Supported observation: Survey respondents discussed fraud use cases, data governance, explainability and integration constraints.

Proposed design response: Design interpretable evidence and realistic integration boundaries rather than citing adoption as customer demand.

## Where the idea came from

The combination is a proposed research program: payment-risk ranking, time-correct evidence, uncertain delayed outcomes, explicit reviewer capacity and local graph ablations. Each component has prior work. No novelty claim has been established by this source review. A future paper must compare the exact method to closest literature and explain the remaining contribution, which may be a benchmark, a reproducibility result or a failure analysis rather than a new model family.

The currently relevant 2026 FATF and payment-fraud material strengthens the problem motivation, while methodological sources determine experiment design. Neither institutional concern nor large fraud losses is evidence that this particular project can obtain funding. The present goal is a technically defensible artifact and an honest research question.
