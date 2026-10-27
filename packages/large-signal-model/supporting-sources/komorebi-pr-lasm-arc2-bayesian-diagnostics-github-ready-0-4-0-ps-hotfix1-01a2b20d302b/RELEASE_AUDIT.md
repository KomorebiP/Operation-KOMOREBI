# Release audit

**Release:** PR-LASM ARC2 Bayesian Entry 0.4.0  
**Author:** Komorebi P.

## Implemented model

Version 0.4.0 implements a finite static Bayesian realization of the Projector-Resolved Large Algebraic Signal Model for ARC-AGI-2:

- exact spatial, color, unitary Fourier, orthonormal Haar, polyphase 2/3/4, and object-relational atlases
- separate 48-coordinate macro, 96-coordinate meso, and 192-coordinate micro statistical states
- typed base, projector, structural, residual-refinement, and fallback program families
- hierarchical Beta family and route reliability posteriors
- Bayesian ridge reliability calibration with covariance and predictive variance
- normalized posteriors over programs, families, atlases, resolutions, and output grids
- posterior-diverse two-attempt selection
- exact array equality as the final correctness contract

Version 0.4.0 adds marker-glyph recoloring, enclosed-region filling, periodic resizing, Kronecker motif variants, modular affine tiling, object-chain packing, object shape and hole conditioned recoloring, and periodic stripe construction. It also adds a complete problem/solution diagnostic atlas.

PowerShell hotfix 1 replaces shell-function-dependent `conda` calls with direct executable discovery, supports clean `-NoProfile` child processes, accepts `-CondaExecutable`, validates required inputs, and propagates Conda failures without relying on stale `$LASTEXITCODE` state. The Python solver and frozen runtime hashes are unchanged.

## Automated validation

| Check | Result |
|---|---:|
| Repository tests | **31 passed** |
| Synthetic solver regression | **6/6 exact** |
| Synthetic ARC-shaped file pipeline | **6/6 exact** |
| Self-contained notebook execution | **6/6 workers, valid submission** |
| Official training smoke, first 25 tasks | **14/25 outputs exact** |
| Hard-isolated official test smoke | **25/25 workers, 0 timeouts, valid submission** |
| Wheel build and isolated installation | **passed** |
| Installed-wheel self-test | **6/6 exact** |
| Source distribution and rebuild | **passed** |
| Randomized exact-atlas audit | **128 grids passed** |
| Largest reconstruction residual | **1.1546319456101628e-14** |
| Independent public-training rerun | **108/1,000 whole tasks; 119/1,076 outputs exact** |
| Output rate | **11.0595%** |
| Attempt 1 exact | **112/1,076** |
| Attempt 2 exact | **7/1,076** |
| Submission schema | **valid** |

The diagnostic audit classifies 929 misses as operator or representation coverage failures and 28 as posterior-selection or few-shot-generalization failures. Of 957 missed outputs, 846 have the correct dimensions but incorrect cells, and 111 also have the wrong dimensions.

## Bayesian calibration and generalization ledger

The model was fitted only from the public training split. A deterministic task-ID hash assigns 799 tasks to fitting and 201 tasks to a parameter holdout.

| Audit | Whole tasks | Exact outputs | Output rate |
|---|---:|---:|---:|
| Calibration partition | 77/799 | 86/857 | 10.0350% |
| Parameter holdout | 30/201 | 32/219 | 14.6119% |
| Partition combined | 107/1000 | 118/1076 | 10.9665% |
| Independent full rerun | 108/1,000 | 119/1076 | 11.0595% |
| Historical 0.3.0 rerun | 89/1,000 | 100/1,076 | 9.2937% |

On the fixed holdout, Bayesian and deterministic selection both solve 32/219 outputs; the candidate-oracle union solves 33/219.

## Diagnostic outputs

A scored run can emit:

```text
index.html
summary.json
output_ledger.csv
near_misses.json
problems_and_solutions.jsonl
tasks/<task_id>_<test_index>.html
tasks/<task_id>_<test_index>.svg
tasks/<task_id>_<test_index>.json
```

Each record includes demonstrations, test input, expected solution, both attempts, mismatch maps, color-confusion tables, first mismatch coordinates, selected programs, posterior support, and a failure-stage diagnosis. Partial agreement remains diagnostic only and does not alter ARC exact scoring. The PowerShell runner accepts `-DiagnosticLimit 0` to render every scored output.

## Claim boundary

Version 0.4.0 is mechanically ready for offline execution and Kaggle packaging, but it is not competitively ready. Typed transformation-language coverage remains the principal limitation. No public-evaluation or private competition score is reported.
