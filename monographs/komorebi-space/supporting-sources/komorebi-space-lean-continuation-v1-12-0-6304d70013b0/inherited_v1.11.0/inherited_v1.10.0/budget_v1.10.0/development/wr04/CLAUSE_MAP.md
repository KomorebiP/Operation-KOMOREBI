# WR04 sharp budget duality: implementation and verification

Source: `formal/KomorebiSpace/BudgetDuality.lean`

Initial accepted source SHA-256: `c79f643994957cd05b067da3a5f52e8530d1e2d332f72a7ddeb8486273d834ce`

The public setting is a bounded real linear map `T : H →L[ℝ] Y` between complete real Hilbert spaces, fixed data `r`, and a nonnegative correction budget `M`. The norm is the given Hilbert norm. There is no finite-dimensional, separable, injective, closed-range, positive-budget, or nonzero-residual assumption.

| Printed WR04 clause | Lean theorem | Evidence |
|---|---|---|
| Every unit-ball dual vector bounds every feasible candidate residual | `dualValue_le_residual` | Adjoint identity and two Cauchy–Schwarz inequalities |
| Every dual value is at most the budget profile | `dualValue_le_beta` | Evaluate the candidate bound at the WR03 attaining minimizer |
| The normalized minimizing residual is a supporting witness | `minimizer_variational`, `exists_sharp_witness_of_variational` | Mathlib's convex projection variational characterization and an explicit Hilbert-ball support computation |
| The dual bound is attained for every nonnegative budget | `exists_attaining_dual_witness` | WR03 minimizer supplies the variational helper's hypotheses |
| The displayed optimization is a maximum, not only a supremum | `sharp_budget_duality` | Literal `IsGreatest` of the image of the closed unit ball |
| A value strictly above epsilon rules out every correction meeting both bounds | `strict_exclusion_certificate` | Contradiction with the universal candidate bound |

The auxiliary theorem `ball_support_eq` proves the exact support value `M * ‖g‖`. Its proof separates `g = 0`. Otherwise it uses the admissible vector `(M / ‖g‖) • g`, which is also valid at `M = 0`.

The witness theorem first separates zero minimizing residual and chooses `z = 0`. For nonzero residual `v`, it chooses `z = ‖v‖⁻¹ • v`, proves `‖z‖ = 1`, derives the support-maximization property from the variational inequality, and substitutes the exact support value. No optimizer or support equality is assumed by the final WR04 theorem.

## Compiler and axiom records

The isolated full module passed attempt `005`, with `-j1`, `-DwarningAsError=true`, and `-DautoImplicit=false`. Its log is empty and exit code is zero. This run imported the then-compiled WR03 module. The later integrated replay is the authoritative evidence for the final combined revision.

Attempt `006` imported the accepted WR04 object and printed all eight explicit theorem types and axiom dependencies. All eight depend only on `propext`, `Classical.choice`, and `Quot.sound`. Exact output is retained in `attempts/006/compiler.log`. This preliminary probe does not replace the independent full-declaration audit or integrated replay.

## Failed attempts and corrections

| Attempt | Outcome | Diagnosis and correction |
|---|---|---|
| `001` | Failed | The warning-as-error gate caught an unnecessary completeness assumption on `ball_support_eq`. An inner-product symmetry rewrite also used the wrong argument orientation. Removed the unused assumption with `omit` and used a typed symmetric inequality. |
| `002` | Failed | The documentation comment preceded `omit`, which Lean's parser rejected. Moved `omit` before the comment. |
| `003` | Passed | The three independent helper theorems compiled. |
| `004` | Failed | The warning-as-error gate caught unnecessary completeness assumptions on the variational helper. Its hypotheses already provide a minimizer. Removed those assumptions from that helper. |
| `005` | Passed | Full WR04 module, including sharpness, literal maximum, and exclusion. |
| `006` | Passed | Eight theorem type and axiom probes. |

Every attempt has an immutable source copy, compiler log, source/log hashes, exact command, search path, elapsed time, and exit code. No failure has been erased or labeled as a passing verification.

## Scope and remaining gates

This is a proof of WR04 over the specified Hilbert setting. It does not claim an executable numerical solver, a computable maximizer, or a certificate bridge for floating-point arithmetic. The code uses classical choice in existing Hilbert-space existence machinery. The parent workstream owns independent type/mathematical review, positive boundary examples, rejection controls, and fresh integrated replay before release acceptance.
