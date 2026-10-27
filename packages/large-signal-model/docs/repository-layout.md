# Repository layout

| Path | Purpose |
|---|---|
| `src/komorebi_pr_lasm` | Public facade, continuous signal runtime and source-signal persistence. |
| `src/komorebi_arc3_offline` | Inherited implementation, exact atlas, packet tree, Bayesian model and graph. |
| `tests` | Original tests and new numerical-contract/regression tests. |
| `examples` | Worked reconstruction, refinement, signal, FIR, streaming, archive, operator and integer bridge examples. |
| `scripts` | Reproducible stress tests, source checks and an installed-backend offline build. |
| `docs` | Current guide, figures, API and migration documentation. |
| `paper` | Unchanged 38-page historical capstone and original sources/figures. |
| `benchmarks/reference` | Versioned historical evidence, not current performance claims. |
| `verification` | Current raw logs, row-level ledgers, source hashes and the execution record. |
| `environment_files` | README only. Optional local game sources are excluded. |
| `test_environment_files` | Small repository-owned mock fixture trees for regression tests. |

The broader reconstruction corpus and old ARC2 diagnostic archive are preserved as
separate companions in the full handoff, not imported into the core runtime.
