# 04 — Evaluation protocol

## Hypothesis and primary endpoint

H1: adding time-correct behavioral and local graph features improves recall at a fixed daily review capacity compared with the strongest predeclared tabular baseline, without worsening modeled review cost beyond the preregistered tolerance. The null is no useful improvement. This document proposes the experiment and contains no results.

Use offline daily batch ranking first: after the day's authorized observations are assembled, each transaction has its own frozen as-of score; the queue selects the highest scores from that day. Ranking at day-end is not a real-time intervention simulation. If a future experiment claims online prevention, define a sequential policy with a budget state and evaluate it separately. Do not retrospectively select the day's top K and claim those payments could have been blocked in advance.

## Partition calendar and label maturity

The reference chronology spans 540 days including explicit label-maturity intervals. These are synthetic design choices, not industry feedback-delay claims. Day numbers identify UTC calendar days from a preregistered origin; intervals are half-open timestamp ranges. Freeze exact boundaries and all label-availability cutoffs in the run manifest.

| Stage | Observation days used for that stage | Maturity interval | Knowledge cutoff / artifact freeze | Next observations permitted |
| --- | --- | --- | --- | --- |
| Training and preprocessing fit | 1–100 | 101–160 | End of day 160 | Model-selection scoring starts day 161 |
| Model / hyperparameter selection | 161–190 | 191–250 | End of day 250 | Calibration scoring starts day 251 |
| Probability calibration fit | 251–270 | 271–330 | End of day 330 | Policy-validation scoring starts day 331 |
| Review-policy / cost-based choice | 331–360 | 361–420 | End of day 420 | Final-test scoring starts day 421 |
| Final held-out evaluation | 421–480 | 481–540 | End of day 540; evaluation only | No artifact changes from these labels |

Every supervised choice requires `label.status == resolved` and `label.available_at <= that_stage.knowledge_cutoff`, including model selection, hyperparameter choice, calibrator fitting and policy selection. Filter labels before the stage process starts and give it only its authorized partition. Preprocessing and candidate estimators fit exclusively on training rows and labels available by day 160. Select among these fitted estimators by day 250; do not refit on selection or calibration observations. Fit calibration by day 330 using the selected frozen model. Choose policy by day 420 using the already frozen calibrator. Hash all preprocessing, feature definitions, models, calibration, policy and tie rules by day 420, before the first final-test score. Future-held-out labels cannot affect any of them.

Maturity-interval observations may contribute unlabeled, time-correct history to subsequent feature calculations; they do not become extra supervised fit or selection rows. Store their role explicitly. A label arriving after its stage cutoff remains unavailable to that stage even if it arrives before some later cutoff. The 60-day intervals permit the proposed delay distributions to mature without using future test knowledge, but unresolved outcomes and longer delays can still remain.

Preregister minimum overall and class-count coverage separately for each stage. The default design gate is at least 90% resolved outcomes and at least 30 resolved positives and 30 resolved negatives in every stage used for training, model selection, calibration or policy choice; these are planning floors, not a guarantee of precise estimates. Require the same 90% coverage before a primary final-test comparison and report class counts. Below a gate, stop that comparison and record `insufficient_label_coverage`; report descriptive bounds only. Do not retroactively move cutoffs, invent negative labels or select a different maturity window after observing final-test performance. A revised schedule is a new preregistered experiment with new untouched final-test data.

Label-delay sensitivity uses distributions parameterized around 1, 7, 30 and 60 days, plus an explicitly unresolved or longer-delay tail; it does not assume every label appears at one fixed delay. Report label coverage at every decision stage. Early-training tests may separately quantify the effect of shorter maturity windows. All fitting and decision timestamps must precede the relevant forward-scoring period. Zero unresolved labels is a special generator setting and must be disclosed.

Two independent evaluation tracks are required. The temporal warm-entity track permits a customer's legitimate past history to inform their future transactions, as would be possible in that setting. It does not permit future edges or labels. The strict cold-entity track creates disjoint synthetic graph components assigned before generation; no account, beneficiary, device or edge can bridge train and test. Report the extra artificiality of removing shared merchants. Never describe ordinary chronological overlap as entity-isolated generalization.

## Datasets and repeated experiments

Start with 10,000 events for smoke runs, then preregister a reference size such as 250,000 events and a fraud-prevalence range. Those are targets, not measured data. Retain natural generated prevalence in evaluation. If rebalancing helps training, it occurs only inside the training pipeline. Run at least five prespecified generator seeds with the same model-search budget; choose seeds before seeing outcomes. Use development seeds for iteration and unseen seeds for the final study. A second generator configuration with different legitimate distributions tests dependence on simulation shortcuts.

The supplied small examples are public development specifications, never the held-out benchmark. At least 60 independently authored or withheld functional cases should cover temporal, identity, input, labeling, queue and report behavior. Their IDs and hashes go in a reviewer-owned manifest; the model process cannot read oracle files.

## Baselines and ablations

B0 constant/prevalence score and seeded random tie ranking; B1 transparent rules; B2 regularized logistic regression; B3 gradient-boosted trees on current-transaction and permitted base context; C1 B3 plus behavior history; C2 C1 plus local graph aggregates. Compare the best B baseline chosen on model-selection data against a candidate chosen there under equal budgets. Calibration is fitted only on its own period using labels available by its stage cutoff; any allowed threshold, capacity or cost-based policy choice uses only policy-validation labels available by its later cutoff. The primary capacity and cost sensitivity grid remain preregistered; if alternative policies are compared, their selection rule is also declared in advance. Final-test results cannot change any artifact or decision. Every stage process receives only its own eligible observations and labels.

No fraud label, future disposition, chargeback flag unavailable at decision time, fraud-type string, future edge count or generator branch ID enters a feature. Account IDs are join keys, not model inputs. Report input-feature lists and evidence timestamps to expose shortcuts.

## Metrics and denominators

The primary capacity is a preregistered review fraction, for example 1% of eligible transactions per UTC day; it is a synthetic evaluation convention. Secondary sensitivity at 0.1%, 0.5% and 2% is declared before final runs. Use K = floor(rate × eligible daily count), allowing K=0, and deterministic hash tie breaks. Do not silently round up a one-review minimum, which changes the budget for small cohorts. A fixed absolute K is an optional additional analysis.

Call the resolved-only point metrics `precision_resolved@K = S_pos / S_resolved` and `recall_resolved@K = S_pos / P_resolved`, where S_pos is selected resolved positives, S_resolved is all selected resolved rows, and P_resolved is all resolved positives. Unknown outcomes consume queue capacity but are excluded from these point-estimate denominators. These resolved-subset metrics do not by themselves estimate full-population quality when label missingness is informative. Zero denominators yield null with an explanation.

Also disclose `S`, the actual number selected; `U_s`, selected unresolved count; and `U_u`, unselected unresolved count. Full-population precision bounds are `[S_pos / S, (S_pos + U_s) / S]` when S > 0. With positive defined denominators, recall bounds are `[S_pos / (P_resolved + U_u), (S_pos + U_s) / (P_resolved + U_s)]`. The lower endpoint treats unselected unknowns as fraudulent and selected unknowns as legitimate; the upper endpoint uses the reverse assignment. If an endpoint has no possible positive denominator, mark the corresponding recall bound undefined and the comparison inconclusive, rather than forcing a zero or one. Do not present resolved-only point metrics as population performance even if the coverage gate passes.

The `unknown-capacity-cost` example in examples/evaluation-boundaries.json makes the distinction concrete: four selected rows contain one resolved positive, one resolved negative and two unknowns. Resolved precision is 1/2; population precision is bounded by 1/4 and 3/4. Its two unselected rows include one resolved positive and one unknown. Resolved recall is 1/2; population recall lies between 1/3 and 3/4. Selected unknowns occupied two real review slots. These are hand-calculated specifications, not model results. Below the stage's preregistered maturity gate, report incomplete coverage and bounds without a definitive comparison.

Report noninterpolated average precision (AP) using the documented implementation. If reporting trapezoidal area under the precision-recall curve, label it separately; AP and interpolated PR-AUC are not interchangeable. ROC-AUC is secondary and cannot substitute for workload metrics. Include false-positive rate on resolved legitimate transactions, unique legitimate accounts alerted, repeat-alert burden and positive prevalence. Zero-positive slices report null recall/AP with explanation.

Amount-weighted recall = sum(amount of selected confirmed synthetic fraudulent payments) / sum(amount of all confirmed synthetic fraudulent payments), within one currency. It is captured exposure, not recovered funds. Brier score and reliability plots require genuine calibrated probabilities; raw anomaly scores get ranking metrics only. Show calibration-bin counts and do not present tiny-bin estimates as reliable.

## Cost sensitivity and uncertainty

Use the explicitly named known-outcome subtotal `C_known = r × S + f × S_legit + m × A_unselected_fraud`, where r is cost per review, f is additional false-alert cost per selected legitimate payment, m is assumed missed-loss fraction, S includes every selected payment including unknowns, S_legit counts selected resolved legitimate payments, and A_unselected_fraud sums unselected resolved fraudulent amounts. All costs and amounts use the same currency and minor-unit convention. Nonnegative r, f and m are required, and m lies in [0,1]. This subtotal is not a full-population cost estimate when labels are unresolved.

Let U_s be selected unknown count and A_unselected_unknown the total amount of unselected unknown payments. Under this model, full-population cost is bounded by `C_lower = C_known` and `C_upper = C_known + f × U_s + m × A_unselected_unknown`. A selected unknown can add a false-alert cost if legitimate; an unselected unknown can add missed loss if fraudulent. Both kinds must appear in the report, with counts and amounts. The formulas intentionally describe modeled cost under an assumed decision-effect convention, not actual recovery or proven prevention. Other intervention costs or imperfect detection after review require an explicitly expanded model.

In the supplied six-row specification, r=100, f=500 and m=1 in minor units; four rows are selected, one selected resolved row is legitimate, and the unselected known fraudulent payment is 4000. Thus C_known=C_lower=4900. Two selected unknowns can add 1000, and one unselected unknown of 5000 can add 5000: C_upper=10900. A report omitting the latter term is incorrect. Label-dependent bounds are not a confidence interval.

Compare candidate and baseline under the same cost grid. Report resolved-outcome comparisons as conditional. A sufficient conservative condition for full-population superiority is candidate upper bound < baseline lower bound; otherwise withhold that claim. A tighter optional paired bound may optimize cost differences per transaction using the same unknown truth assignment for both policies, but independent optimistic truth assignments must never be compared as if consistent. No claim of realized financial savings follows from this model.

### Paired bootstrap estimand and queue recomputation

The primary uncertainty estimate is conditional on the frozen fitted model, its frozen historical feature context and the generated observation window. It estimates variation when independent synthetic transaction-network components are resampled from that evaluation population, while applying the same daily review-rate policy again. It does not estimate model-retraining uncertainty or establish generalization to real financial systems. Variation across prespecified generator seeds is reported separately.

Define connected components from the synthetic generator's actor/payee/device membership before examining labels or predictions, and preserve each component's complete evaluation timeline. Use at least 1,000 paired component bootstrap replicates with a fixed seed. If one giant component or too few independent components makes this estimate unreliable, show the component-size distribution and mark the interval unavailable; do not replace it silently with an independence assumption. Account-cluster resampling is an explicitly exploratory sensitivity only when cross-account dependence is acknowledged.

For each replicate, sample the same number of components with replacement. Each draw receives a unique clone index; clone every row and identifier within the drawn component consistently, retaining its timestamps, frozen scores, labels and amounts. A repeated component is a separate bootstrap copy, not a duplicate transport event to discard. Use the identical sampled components and clone map for candidate and baseline. Do not recompute graph features or refit models on this resample: the estimand is conditional on their original information context. Bootstrap clone references point back to immutable original evidence and are not new financial observations.

For each calendar day in each replicate, recompute N from all cloned eligible rows, including unresolved ones, set K=floor(rate × N), rerank separately by each frozen model's score and select min(N,K) rows. Preserve deterministic original tie hashes, appending clone index as the secondary tie key; never sort by label. Empty days or K=0 remain empty and metric denominators are handled explicitly. Compute that replicate's metric and cost difference, using its own selected/resolved/unknown counts. Carrying over original selected flags estimates a different fixed-queue quantity and is prohibited for the primary interval. The supplied `bootstrap-rerank` example doubles one component, recomputes K and changes the selected rows and proves that reusing original selections gives the wrong answer.

Show the paired 95% interval for the predeclared primary difference only when denominators and component counts support it. Secondary slice findings remain exploratory unless the preregistration handles multiplicity. Report interval method, valid/invalid replicate counts, cluster sizes, seeds, and the number of zero-positive or zero-review replicates. Failures are not silently resampled away.

## Drift and subgroup checks

Shift transaction frequency and amount distributions, introduce new payees, increase legitimate high-value activity and hold out a risky mechanism from training. Keep drift metadata inaccessible to scorers. Report pre-shift and post-shift quality, review saturation, label coverage and calibration. No automatic retraining on final labels. A retraining study needs its own forward-chaining protocol with fit times and label availability.

Predeclare slices for new versus established accounts, sparse versus dense history, amount bands, shared versus uncommon payees and device-known versus device-missing. Include class counts and intervals; under 30 positives is explicitly exploratory, not a universal statistical guarantee. Synthetic slices do not establish fairness for any real demographic group.

## Completion versus positive scientific result

Engineering completion requires the contract, leakage, security and metric tests to pass; all planned models to be evaluated; failures to be disclosed; and an independent reproduction. A positive H1 claim additionally requires the predeclared improvement and cost criteria on final data with uncertainty reported. If the candidate loses, publish that result with a clear error analysis. No comparison here establishes industry performance, institutional approval or research novelty.
