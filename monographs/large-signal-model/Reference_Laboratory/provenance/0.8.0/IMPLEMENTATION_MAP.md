# Implementation map — foundations 0.8.0

The programs are reference calculations, not a production implementation of every proposition.

| Result | Executed component | Boundary |
|---|---|---|
| Proposition 80, fixed repair bracket | `examples/reduced_repair_example.py`, `examples/replay_reduced_repair.py` | Reuses previous geometry and exact polynomial checker; no global optimization. |
| Proposition 81, sequential confidence | Scalar arithmetic in `checks/data_certificate_reference.py` | General vector theorem is written, scalar example executed. |
| Proposition 82, moment-to-operator sets | Proof and exact identity checks | No general hidden-state or multi-action regression learner. |
| Proposition 83, moment cone and likelihood model | `checks/data_supported_checks.py` | Dictionary, domain and finite family supplied. |
| Proposition 84, rational intervals | `examples/dependent_data_certificate.py` | Saved exact discrete observations; assumptions not authenticated by replay. |
| Propositions 85–86, record and marginal budgets | `checks/data_certificate_reference.py`, exact finite marginal checks | Autonomous scalar Markov example, not arbitrary policy memory. |
| Proposition 87, integrated data-to-domain statement | `examples/replay_dependent_data_certificate.py` | Exact arithmetic and full-family certificate; conditional statistical coverage. |

`examples/dependent_signal_generator.py` is separate from inference and records its true parameters separately. The inference example consumes only saved node indices, the reference measure and the declared model.

`certificates/reduced_repair_certificate.json` and `certificates/reduced_repair_comparison.json` are independent domain witnesses. `certificates/dependent_data_certificate.json` records data fingerprint, sufficient statistics, rational outer confidence bounds, whole-box validity and comparison budgets. A valid replay cannot certify that an unknown physical process obeys the model assumptions.

The earlier production package is not modified. All older reference suites remain separately identifiable, and historical evidence is under `verification/prior_070/` or inside the unchanged predecessor archive.
