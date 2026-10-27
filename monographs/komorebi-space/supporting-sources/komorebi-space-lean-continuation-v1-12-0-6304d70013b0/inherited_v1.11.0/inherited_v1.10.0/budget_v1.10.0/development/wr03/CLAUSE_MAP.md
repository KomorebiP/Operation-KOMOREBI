# WR03 core implementation handoff

Frozen production source: `budget_v1.10.0/formal/KomorebiSpace/BudgetProfile.lean`.

SHA-256: `a11931c108e046080539e346bbf910a99395da0ee51dc8634f8101bb9c95170f`.

The source compiles with Lean 4.34.0-rc2, `-j1`, `-DwarningAsError=true`, and `-DautoImplicit=false`. The final successful production run is `attempt_007/receipt.json`; its empty compiler log is retained. `attempt_008/receipt.json` records the successful public declaration and axiom export. `PUBLIC_TYPES.txt` extracts the 21 exact public types from that compiler output; the unabridged output remains in `attempt_008/compile.log`.

This is a development handoff, not the independent acceptance report or fresh integrated replay. The geometry owner separately implements the nonincreasing, convex, Lipschitz, and zero-budget clauses in `BudgetProfileGeometry.lean`.

## Clause correspondence

All declaration names below have prefix `KomorebiSpace.BudgetProfile.`.

| Printed or contract clause | Declaration | Source line |
|---|---|---:|
| Distance-to-budget-image definition | `beta` | 29 |
| Convex fixed-budget image | `convex_budget_image` | 33 |
| Closed fixed-budget image without closed-range assumption | `isClosed_budget_image` | 38 |
| Nonempty image for every nonnegative budget | `budget_image_nonempty` | 53 |
| Nonnegative profile | `beta_nonneg` | 58 |
| Profile bounded by any feasible residual | `beta_le_residual` | 62 |
| Attainment at the same budget | `exists_budget_minimizer` | 70 |
| Equivalence to the printed infimum over feasible corrections | `beta_eq_iInf` | 79 |
| Exact closure of the operator range | `rangeClosure`, `rangeClosure_coe` | 90, 94 |
| Projection onto that closed subspace | `projectedDatum`, `projectedDatum_mem` | 101, 105 |
| Range elements belong to that closure | `apply_mem_rangeClosure` | 110 |
| Printed orthogonal residual decomposition | `residual_sq_decomposition` | 115 |
| Projected residual equals distance to the closure of the range | `projected_residual_eq_infDist` | 126 |
| Unrestricted floor bounds every nonnegative budget profile below | `floor_le_beta` | 135 |
| Finite-budget floor equality iff projected datum is feasible in that budget | `beta_eq_floor_iff` | 144 |
| Zero profile iff exact datum is feasible in that budget | `beta_eq_zero_iff` | 159 |
| Real-budget limit at infinity equals distance to range closure | `beta_tendsto_infDist` | 172 |
| Same limit in the printed projected-residual notation | `beta_tendsto_floor` | 192 |

The additional public instance `rangeClosure_completeSpace` supplies completeness of the closed range subspace from completeness of the target. It does not assume the unclosed range is complete.

## Mathematical scope

The production source is quantified over arbitrary real Hilbert spaces. Fixed-budget attainment and the two feasibility equivalences assume completeness of source and target exactly as in the contract; there are no finite-dimensional, separability, injectivity, or closed-range assumptions. Several auxiliary estimates and the limiting statement are proved with fewer assumptions, with the unused completeness assumptions explicitly omitted rather than silently generalized in the public documentation.

For nonnegative budgets, `beta_eq_iInf` certifies that the metric distance definition is the printed infimum. The profile is defined for all real arguments because the limit uses real budgets; every finite-budget feasibility theorem retains `0 ≤ M`. No assertion about the intended optimization meaning for negative budgets is made. The zero budget is included by all nonnegative-budget theorems. The theorem statements allow the zero vector space; vector-space structure supplies a zero element, so an empty carrier cannot satisfy the declared typeclasses.

Closedness is proved by lifting a convergent image sequence to the actual correction ball and applying the accepted same-budget WR01 theorem. This invokes its weak-star compactness route and does not require a weak subsequence theorem. Hilbert projection onto the closed convex image then supplies the minimizer. The finite-floor characterization uses the orthogonal square identity, and the limiting proof chooses a single approximate range element for each epsilon, which is feasible at all sufficiently large real budgets.

There are 3 explicit definitions, 17 explicit theorems, and 1 explicit instance. All 21 public declarations were queried for transitive axioms; the union is exactly `Classical.choice`, `Quot.sound`, and `propext`. This public-declaration check is separate from the parent's environment-wide declaration audit.

## Preserved failures and recovery

Every attempt has an immutable source snapshot, command/environment receipt, compiler log, SHA-256, exit code, elapsed time, and source-unchanged check in its numbered directory.

| Attempt | Result | Explanation |
|---|---|---|
| 001 | Failed | Lean resolved the first `KomorebiSpace` prefix directory and did not fall through to the inherited module. No proof was elaborated. The local development build was populated with symlinks to accepted inherited objects, without changing them. |
| 002 | Passed | Initial fixed-budget API: definition, convexity, closedness, comparison, attainment. |
| 003 | Failed | The newly defined range closure needed an explicit completeness instance for orthogonal projection. One unused source-completeness assumption was also reported by the linter. Consequent elaborator-generated `sorry` diagnostics were not source proof placeholders. |
| 004–005 | Failed | A projection infimum identity needed explicit conversion between the submodule subtype and its underlying-set subtype. |
| 006 | Failed diagnostic run | Printed elaborated types for that same conversion issue. No mathematical statement was changed. |
| 007 | Passed | Complete assigned WR03 core; conversion made explicit with `change`. |
| 008 | Passed | All public types, proof terms, and transitive axiom dependencies exported. |

Only the assigned new source and `development/wr03` were written. Historical sources, runtime files, accepted base objects, and the shared ledger were not modified.
