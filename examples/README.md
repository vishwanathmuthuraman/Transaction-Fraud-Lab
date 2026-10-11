# Original synthetic development scenarios

These are hand-authored behavioral specifications. They are not sampled financial records, benchmark results or evidence that a model detects fraud. The `measured_model_result` field is null in every expected file.

Each `.case.json` has a matching `.expected.json`. The combined case is for a human reviewer and the documentation checker; the future application must separate oracle labels from observations before launching its scoring process. File names, descriptions and expected results must never become model features.

Eligible history in expected files means all same-organization prior events visible to the current decision, before filtering to a particular sender's behavioral feature. The application must perform that additional sender/recipient filtering as specified in its feature contract. Duplicate errors, scope errors and unsupported currency mixing stop before history extraction. Eligible training label IDs use the separate fit cutoff.

The documentation validator checks schema conformance and these simple specified eligibility sets. It does not implement the research model, run application acceptance tests or assess predictive quality.

- **ordinary-history:** One known prior payment and one current payment. [Case](ordinary-history.case.json) · [Expected specification](ordinary-history.expected.json)
- **future-event:** A later payment is present in the input file. [Case](future-event.case.json) · [Expected specification](future-event.expected.json)
- **late-arrival:** A prior occurred payment only becomes available after scoring. [Case](late-arrival.case.json) · [Expected specification](late-arrival.expected.json)
- **simultaneous-event:** Another payment shares the current occurrence timestamp. [Case](simultaneous-event.case.json) · [Expected specification](simultaneous-event.expected.json)
- **delayed-label:** Fraud label becomes known after the fit cutoff. [Case](delayed-label.case.json) · [Expected specification](delayed-label.expected.json)
- **unresolved-label:** Prior outcome is unresolved. [Case](unresolved-label.case.json) · [Expected specification](unresolved-label.expected.json)
- **conflicting-duplicate:** Two records reuse an ID with different amounts. [Case](conflicting-duplicate.case.json) · [Expected specification](conflicting-duplicate.expected.json)
- **exact-duplicate:** Identical replay occurs twice. [Case](exact-duplicate.case.json) · [Expected specification](exact-duplicate.expected.json)
- **cross-organization-context:** Scoring context contains a second organizations account history. [Case](cross-organization-context.case.json) · [Expected specification](cross-organization-context.expected.json)
- **mixed-currency:** Two currencies would enter the same R1 experiment. [Case](mixed-currency.case.json) · [Expected specification](mixed-currency.expected.json)
- **cold-start:** A new account has no prior history and no device. [Case](cold-start.case.json) · [Expected specification](cold-start.expected.json)
- **payroll-hard-negative:** High legitimate outgoing activity challenges naive velocity rules. [Case](payroll-hard-negative.case.json) · [Expected specification](payroll-hard-negative.expected.json)
- **shared-payee-negative:** Distinct legitimate senders pay a common merchant. [Case](shared-payee-negative.case.json) · [Expected specification](shared-payee-negative.expected.json)
- **future-graph-edge:** A future edge would create a stronger network motif. [Case](future-graph-edge.case.json) · [Expected specification](future-graph-edge.expected.json)
- **censored-observation:** The current outcome has not matured by observation end. [Case](censored-observation.case.json) · [Expected specification](censored-observation.expected.json)
- **limited-review-capacity:** A one-payment daily cohort at a 1 percent floor budget has K zero. [Case](limited-review-capacity.case.json) · [Expected specification](limited-review-capacity.expected.json)

## Hand-calculated evaluation boundaries

[Evaluation specifications](evaluation-boundaries.json) cover four supervised-stage knowledge cutoffs, a label-coverage gate, resolved-versus-population precision/recall, cost bounds including unselected unknown loss, and a paired component-bootstrap replicate whose daily queue must be recomputed. These are oracle specifications for future application tests. The documentation checker verifies their internal arithmetic and chronology; it does not implement or validate an application model.
