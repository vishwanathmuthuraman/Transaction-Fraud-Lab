# 09 — Data contracts and security

## Payment observations

Each payment contains `payment_id`, `organization_id`, `sender_id`, `recipient_id`, `occurred_at`, `available_at`, `amount_minor`, `currency`, `channel` and nullable `device_id`. R1 input comes from original synthetic generation. Identifiers use a synthetic prefix. The scoring context supplies `scoring_at` and `current_payment_id`; it cannot override organization scope. No name, email, phone, card number, account number, address or raw memo is necessary for the initial algorithm.

The JSON Schema rejects additional keys and specifies basic types. Application cross-record validation must additionally check uniqueness, ID references, duplicate equivalence, timestamp relationships, scope, per-experiment currency and current transaction availability. Schema validation alone does not establish time correctness or a valid experiment.

Amounts are integer minor units. The schema permits supported three-letter codes, but R1 experiments use one currency; currency code format is not a guarantee of valid FX conversion. Zero-value transfers can be represented as synthetic edge cases and require an explicit policy. Negative reversals use a separate future event type; do not hide them inside a positive-payment schema.

## Labels and availability

Labels live outside scorer inputs and contain payment_id, organization_id, status, class, available_at and provenance. A resolved class may be `fraudulent` or `legitimate`; unresolved labels have class null and available_at null. Every supervised stage has its own knowledge cutoff; eligible labels must be resolved and available by that stage cutoff. Model-selection, calibration and policy processes must never receive the final oracle directly. Preserve stage role, observation window, knowledge cutoff, freeze timestamp and artifact hashes in the experiment contract; all decision artifacts freeze before first final-test scoring. Final experiment truth belongs to the oracle; a historical fit sees only eligible labels. Label records are versioned in a future implementation; corrections do not mutate already frozen evaluation manifests.

Store a separate generator mechanism catalog inaccessible to all trained models and feature processes. Label availability, case names, scenario descriptions and expected files are forbidden as model features. The supplied cases combine observations and labels for human review and documentation validation only; the application loader must split them at the process boundary before scoring.

## Feature specification

| Feature | Permitted data | Edge case |
| --- | --- | --- |
| Sender count 1h/24h/7d | Prior same-scope outgoing events available at score time | Empty history returns zero plus cold-start flag |
| Sender amount 24h | Same-currency prior outgoing events | No cross-currency summation |
| Payee novelty | Whether sender-recipient pair was previously observed | New pair indicates unfamiliarity, not wrongdoing |
| Amount deviation | Current amount versus prior sender median and robust spread | Insufficient history yields missing plus indicator |
| Recipient fan-in | Distinct prior senders within a bounded eligible window | Shared legitimate payees included as controls |
| Reciprocal/short paths | Bounded prior-edge search | Future edges and other organizations excluded |
| Device novelty | Prior known devices for sender | Missing device is missing, not new by assumption |

Rollup caches include organization, cutoff, feature version and currency. A cache built from full data before splitting is prohibited. Efficient prefix sums are permitted only if their query boundaries reproduce the same eligible historical snapshot.

## Score output and evidence

A future output includes transaction ID, model ID, feature-set version, decision time, score type, finite score, queue rank when assigned, evidence event IDs, reason codes and context flags. Probabilities must be in [0,1]; anomaly values use a distinct type and scale. Reasons describe features such as “first observed payee” and “recent count above prior pattern,” not accusations. Missing context must be visible. A model explanation is not causal proof.

## Local security boundary

No banking credentials or customer data. No outgoing network in evaluation. Canonicalize paths and reject output traversal. Treat all strings as data and escape HTML. Use immutable run outputs and do not load untrusted executable serialization. Avoid notebook outputs containing environment variables. If real data is ever proposed, create a separate private environment and an authorized data-governance plan before ingestion; anonymization claims require more than replacing a name with an ID.
