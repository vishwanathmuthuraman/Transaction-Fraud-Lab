# 07 — Technical risks and limitations

The [risk register](../planning/risks.csv) records open research and engineering concerns. No entry represents a risk resolved by an implemented detector. These limits determine how future results should be interpreted.

| Risk | Why it matters | Required control or disclosure |
| --- | --- | --- |
| Temporal leakage | Future labels or graph edges can make impossible performance look strong | As-of eligibility, separate stage knowledge cutoffs, artifact freezes and leakage tests |
| Synthetic shortcuts | Identifiers, row order or generator branches may expose assigned labels | Hidden generator metadata, overlapping distributions and a changed-generator experiment |
| Selection bias | Reviewed transactions may be more likely to receive labels | Label-coverage reporting, unknown outcome bounds and explicit missingness assumptions |
| Graph contamination | Cross-organization context or future edges may cross a trust boundary | Scoped identifiers, evidence availability and a separate cold-component experiment |
| Queue mismatch | Retrospective daily ranking can be confused with real-time intervention | Label the batch setting; require a distinct forward policy for online claims |
| Metric misuse | Class balance and aggregate accuracy can hide false-alert burden | Natural prevalence, fixed-capacity metrics, explicit denominators and burden counts |
| Dataset mismatch | Account-opening fraud labels answer a different question from payment fraud | State the target and evaluate separate tasks independently |
| Untrusted artifacts | Executable model files or unescaped report content can be unsafe | Provenance checks, constrained formats, escaped reports and no live network action |
| Small-sample inference | Tiny slices and dependent observations can produce unstable conclusions | Counts, component diagnostics, uncertainty and inconclusive-result handling |
| Unnecessary complexity | More languages or model layers can weaken reproducibility | Baselines, profiles and documented tradeoffs before expansion |

## Interpretation limits

A review-priority signal is not a finding of fraud or a claim about a person's intent. Human investigation and independent evidence are required for consequential conclusions. Synthetic evaluation can test controlled methodological properties; it cannot establish operational effectiveness, lawful deployment or fairness for a real population.

Unknown outcomes remain unknown. Missing or insufficiently mature labels can prevent a meaningful comparison even when the documentation and software behave correctly. Modeled review costs describe declared assumptions and do not establish realized savings or prevented losses.

## When to revise the study

If performance disappears after identifiers or generator metadata are removed, examine simulator shortcuts before claiming progress. If graph additions do not improve the frozen endpoint, retain the simpler model. If new legitimate accounts dominate alerts, inspect missing-history behavior and report the burden. If label coverage is insufficient, publish the limits or bounds and design a new preregistered study rather than revise the final evaluation after seeing it.

Only original synthetic examples belong in this research edition. Operational thresholds, customer records and real investigation notes require a separate authorized environment.
