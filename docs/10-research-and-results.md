# 10 — Research plan and result card

## Defensible contribution options

The strongest initial contribution may be an auditable evaluation harness that exposes how temporal leakage, label delay, cold starts and review capacity change apparent model quality. It may instead be a useful feature ablation or a negative result showing that a simpler baseline is more reliable. Do not name an existing combination a novel algorithm without a focused prior-art comparison.

Before drafting a paper, compile the closest methods and compare target, data access, label timing, graph scope, split design, budget policy, metrics, computational cost and limitations. A new name alone is not a contribution. Use external datasets only if the license permits the intended use and their labels actually match the question. BAF concerns account-opening fraud; reproducing it would be a separate task. No external dataset has been downloaded here.

## Planned experiments

E1 tests feature additions against equal-budget baselines. E2 varies feedback delay and unresolved coverage. E3 examines held-out behavior and shifted legitimate patterns. E4 measures warm versus cold entity behavior. E5 measures the cost of false alerts and queue saturation. E6 repeats under a changed generator to expose simulator dependence. The primary endpoint and which analyses are exploratory must be preregistered.

## Result card fields

Title; question; target; dataset and source rights; synthetic assumptions; available evidence at score time; partition dates; label cutoffs; baseline definitions; feature lists; search budget; metric definitions; seeds; hardware; sample counts; actual run IDs; primary result and uncertainty; all null findings; slice limitations; reproduction instructions; failures; threat model; future work. Keep unmeasured fields blank or “not run.”

## Recognition and credibility

A credible submission needs original work, clear related-work positioning, sound experiments, inspectable artifacts and honest authorship. No repository design guarantees funding, institutional certification, a visa result or a research award. Choose a venue only after the evidence and contribution exist. Do not attach an institution's name or logo as an endorsement without actual authorization.

## Relationship to the portfolio

This project demonstrates data engineering, statistical reasoning, security boundaries and disciplined measurement when implemented. It complements a financial-book integrity project because payment screening and accounting investigation use different data, units of analysis, labels and decisions. Keep their result claims separate; a shared contract library later is possible but should not force incompatible targets into one metric.
