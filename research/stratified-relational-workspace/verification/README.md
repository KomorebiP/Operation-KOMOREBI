# Verification suite

The scripts in this directory are regression checks for finite-dimensional identities and examples displayed in the monograph. They do not replace proofs or external review.

## Included checks

| Script | Scope |
|---|---|
| `core_geometry.py` | Holonomy, transfer Laplacians, perturbation bounds, operation leakage, residual transport, gauge covariance, and coarse-graining |
| `case_studies.py` | Human-human, human-AI idealized, and multi-agent analytic examples |
| `decomposition_robustness.py` | Faithful aggregation, two-scale bounds, risk transport, secret-sharing controls, and decomposition envelopes |
| `specification_identifiability.py` | Specification transport, non-identifiability, partial identification, uniform uncertainty, and post-selection inflation |

Run all checks from the repository root:

```bash
python verification/run_all.py
```

Generated outputs are written to `verification/results/` and are ignored by Git. Frozen reference outputs are retained under `verification/baselines/` for inspection. Floating-point values may vary slightly across numerical-library versions, so the scripts enforce theorem-specific tolerances rather than exact byte equality with the baselines.
