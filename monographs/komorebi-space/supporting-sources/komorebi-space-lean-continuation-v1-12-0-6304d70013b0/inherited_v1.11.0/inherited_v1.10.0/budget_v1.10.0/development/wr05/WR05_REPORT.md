# WR05 fixed-budget robustness: implementation record

Base: `KS-v1.9.0-full-monograph-proofread`, as identified in `../../records/BASE_CHECKPOINT.json`.
The frozen target is `../../TARGET_CONTRACT.md` and its verbatim printed statement is `../../records/TARGET_WR03_WR05.tex`.

## Result and scope

The full WR05 target has been implemented in `../../formal/KomorebiSpace/BudgetRobustness.lean` and compiled with Lean 4.34.0-rc2, `-j1 -DwarningAsError=true -DautoImplicit=false`.
The source SHA256 is `1406ffe483fc4de9b5688abea8e84ea2d3b5e48ba4f41127afc230a34c87e87e`.
The clean public-module compilation is `attempts/robustness_002/receipt.json`.
This is development verification. Independent review, rejection controls, and the fresh integrated replay are owned by the coordinating release process.

The public theorems use the same real Hilbert spaces `H` and `Y` for both maps and the same correction budget `M`. The profile comparison uses complete spaces and `0 ≤ M`, without finite-dimensionality, separability, closed range, or injectivity assumptions. The four candidate inequalities do not need completeness. They compare actual Hilbert norms, not coordinates. No statement compares changing preservation kernels.

The norm bounds `‖T-S‖ ≤ η` and `‖r-s‖ ≤ δ` already imply `η,δ ≥ 0`. The profile theorem consequently avoids redundant explicit sign parameters. This strengthens, rather than restricts, the printed hypotheses. Its proof obtains nonnegativity of `η` from the operator norm bound when needed.

## Clause map

All names below are in `KomorebiSpace.BudgetRobustness`.

| Printed clause or proof step | Public declaration | Formal conclusion |
|---|---|---|
| Difference of candidate residual vectors | `candidate_residual_difference_bound` | `‖(r-T a)-(s-S a)‖ ≤ δ + η*‖a‖` |
| Reverse triangle inequality for candidate norms | `candidate_residual_abs_bound` | `abs(‖r-T a‖-‖s-S a‖) ≤ δ + η*‖a‖` |
| Displayed candidate-level uncertainty inequality | `candidate_residual_le` | `‖r-T a‖ ≤ ‖s-S a‖ + δ + η*‖a‖` |
| Uniform allowance on the common feasible ball | `budget_candidate_residual_abs_bound` | For `‖a‖≤M`, the absolute candidate discrepancy is at most `δ+η*M` |
| One direction of the profile comparison | `beta_le_beta_add_uncertainty` | `beta T r M ≤ beta S s M + (δ+η*M)` |
| WR05 absolute profile estimate | `beta_abs_sub_le` | `abs(beta T r M-beta S s M) ≤ δ+η*M` |
| WR05 nominal dual lower certificate | `nominal_dual_lower_certificate` | For `‖z‖≤1`, `inner s z-M*‖S.adjoint z‖-δ-η*M ≤ beta T r M` |
| Consequence for strict robust exclusion | `excludes_budget_of_nominal_dual_certificate` | If the robust nominal certificate exceeds `ε`, every feasible true residual exceeds `ε` |

## Proof dependencies and interpretation

Candidate bounds use subtraction linearity, the operator-norm bound, the triangle inequality, and the reverse triangle inequality. The profile upper comparison evaluates the first profile at a minimizer for the second profile. Reversing the maps and data yields the other direction. There is no assumed correspondence between minimizers.

The nominal certificate combines the lower half of the profile estimate with `KomorebiSpace.BudgetDuality.dualValue_le_beta`. Minima are supplied by `KomorebiSpace.BudgetProfile.exists_budget_minimizer`; each feasible residual bounds its own profile through `beta_le_residual`.

`attempts/audit_001/compile.log` contains the elaborated types, proof terms, and axiom lists for all eight public theorems. `AXIOM_AUDIT.json` records that every dependency list is contained in `propext`, `Classical.choice`, and `Quot.sound`. No admitted theorem or custom axiom was introduced.

## Boundary and falsification evidence

`BoundaryExamples.lean` contains a generic zero-budget theorem, allowing arbitrary operator mismatch, and exact scalar counterexamples to three tempting weakenings:

- Removing `η*M` fails for `T=0`, `S=id`, `r=s=1`, `M=1`.
- Removing `δ` fails for `T=S=0`, `r=1`, `s=0`, `M=1`.
- Replacing `η*M` by `η` fails for `T=0`, `S=id`, `r=s=2`, `M=2`.

These examples use the actual `beta` definition through its verified minimum API. They are exact Lean proofs, not numerical samples. Their successful receipt is recorded separately so they cannot be confused with the eight production declarations.

## Attempt history and corrections

Every compiler invocation preserves a numbered source snapshot, complete compiler log, command, source hash, and exit code under `attempts/`. No failed attempt was overwritten.

| Attempt | Result | What happened |
|---|---|---|
| `candidate_001` | Failed | A deprecated `ContinuousLinearMap.sub_apply` name and two addition-order mismatches were rejected. Used the current `sub_apply` name and explicit `add_le_add` arguments. |
| `candidate_002` | Failed | The strict unused-section-variable linter detected unnecessary completeness assumptions on candidate lemmas. Removed those assumptions from that section. |
| `candidate_003` | Passed | Four candidate inequalities compiled. |
| `comparison_001` | Passed | One-sided and absolute profile comparisons compiled against the verified WR03 API. |
| `robustness_001` | Failed | An inner-product notation scope mismatch affected two declarations. Changed to the plain real-inner notation already used by WR04. |
| `robustness_002` | Passed | All eight public production theorems compiled cleanly. |
| `audit_001` | Passed | Printed types and axiom dependencies for all eight public declarations. |
| `boundaries_001` | Failed | A proposed identical-problem test reduced immediately to `0≤0`, causing strict unnecessary-proof and unused-variable lints. Removed this uninformative test; retained zero-budget behavior and the three substantive falsifications. |
| `boundaries_002` | Passed | Recompiled the retained zero-budget theorem and three substantive exact falsifications. |

No mathematical target was weakened to resolve any failed compilation. No linter was disabled. The public production source was unchanged after its successful `robustness_002` compilation.
