<p align="center"><img src="assets/overview.svg" alt="Transaction Fraud Lab — evidence before accusation; behavior, timing and reviewer capacity" width="100%"></p>

# Transaction Fraud Lab

[![Documentation integrity](https://github.com/vishwanathmuthuraman/Transaction-Fraud-Lab/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/vishwanathmuthuraman/Transaction-Fraud-Lab/actions/workflows/docs.yml)

**An evidence-first research plan for ranking suspicious payments under delayed feedback and limited reviewer capacity.**

A payment may look unusual and still be legitimate. This project asks whether a model can find more simulated fraudulent payments without overwhelming reviewers or treating ordinary customer behavior as wrongdoing.

| Status | Evidence available today |
| --- | --- |
| Design | Requirements, architecture, public milestones and evaluation protocol |
| Examples | Original synthetic cases and expected behavior specifications |
| Validation | Documentation links, schema compatibility, fixture consistency and requirement-to-test coverage only |
| Implementation | Pending — no application, trained model or measured benchmark |
| Distribution | Curated public research specification; license selection pending |

## The research question

Can **time-correct behavioral and local transaction-graph features** improve fraud recall at a fixed review capacity, when feedback arrives late and payment behavior changes? Compare them against transparent rules, logistic regression and a tabular tree model, including hard legitimate cases and unseen entities.

This is a proposed experiment, not an established new algorithm. A carefully measured negative answer remains useful.

```mermaid
flowchart LR
  A[Synthetic payments] --> B[Evidence available at decision time]
  B --> C[Rules and model baselines]
  C --> D[Bounded review queue]
  D --> E[Evidence and uncertainty]
  F[Delayed labels] --> G[Separate evaluation process]
  E --> G
```

## What makes the work worth inspecting

- **No time travel:** future transactions, late labels and future graph edges cannot improve historical predictions.
- **Operational metrics:** recall and precision at a fixed review budget, false alerts, calibration and modeled cost; accuracy alone does not pass.
- **Hard negatives:** payroll bursts, first-time customers and shared merchants must challenge simplistic fraud rules.
- **Honest evidence:** each flagged payment carries the observations used, their timestamps and reasons to doubt the finding.
- **Reproducibility:** frozen splits, generator settings, seeds, hashes, model versions and actual run manifests.

## Start here

[Reading guide](START-HERE.md) · [Engineering policy](ENGINEERING.md) · [Requirements](docs/01-product-requirements.md) · [Public milestones](docs/03-build-plan.md) · [Evaluation](docs/04-evaluation.md)

The Python research implementation is planned. Rust is an optional future inference component only if measurements justify it. There is no live-payment integration, autonomous payment blocking or allegation generation.

## Run the documentation checks

These commands validate this blueprint; they do not train or test a fraud model.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-blueprint.txt
.venv/bin/python scripts/validate_blueprint.py
.venv/bin/python scripts/check_public_docs.py
```

See [source rationale](docs/06-sources-and-design-rationale.md) for the primary research and institutional reports that informed the plan. They do not endorse this project. See [publication boundary](docs/08-publication.md) before making any files public.

## Public package

This edition includes original synthetic examples, contracts, evaluation methods, source rationale and public milestones. Internal task schedules and effort estimates are maintained outside the repository. Implementation and measured algorithm results remain pending. License selection is pending; no code, documentation or data license grant is supplied.

Maintained by [Vishwanath Muthuraman](https://github.com/vishwanathmuthuraman). [Contribution guidance](CONTRIBUTING.md) explains how to propose a synthetic case or challenge a design assumption.
