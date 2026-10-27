# Large Signal Model Lean 0.11.0 — Guide

## Status and scope

38 complete, one partial (P32), 48 not formalized, frozen total 87. Relative to 0.10.0, P33 and P34 are complete. P32 is only partially formalized. The manuscript's written proofs and the status of their Lean translations are distinct. An unfinished Lean obligation is not by itself a counterexample or an open mathematical conjecture.

This release adds four modules, 30 named theorems (eight examples), and four rejection controls. Cumulative inventory: 82 proof modules, 83 compilation targets including the root, 1,338 named declarations, 1,028 named theorems (316 example and 712 supporting), and 76 rejection controls. These are source-index counts; they are not independent results or a measure of scientific completeness.

## P33 — square core reconstruction

`CoreStability.lean` uses the constructed orthogonal pseudoinverse from 0.9.0. The input error satisfies the strict inequality `‖E‖ < rowGain H`. `rowGain` is the inherited variational least row singular value, defined as the infimum of adjoint norm ratios, with the unit-sphere characterization already proved in `IdentificationBound.lean`. This is the same convention used for P16. It is not a new assumed inverse bound or a numerical singular-value calculation.

`core_inverse_laws` proves both inverse identities for the perturbed square core. `coreFit` is `(B H + F) (H+E)†`, now identified with the ordinary inverse estimator under those hypotheses.

The module proves:

- `core_error_identity`: fitted minus true operator equals `(F−BE)(H+E)⁻¹`.
- `core_error_bound`: norm at most `(‖F‖+‖B‖‖E‖)/(rowGain H−‖E‖)`.
- `core_fitted_residual` and `core_fitted_identity`: `(Bhat−B)H=F−Bhat E`, and its right-inverse form.
- `core_fitted_bound`: norm at most `(‖F‖+‖Bhat‖‖E‖)/rowGain H`.
- `core_checked_fitted_bound`: under `‖E‖≤e<rowGain(H+E)`, the denominator may instead be `rowGain(H+E)−e`.

These statements concern a fixed core and exact real linear algebra. They do not establish that finite observations cover the full process, or bound floating-point solve error.

## P34 — normalized filtering

`FilteringStability.lean` works in a real normed state space with a continuous linear mass functional `lam`. The formal name avoids Lean's reserved lambda token. `normalize lam u = (lam u)⁻¹ • u`; all semantic normalization theorems supply nonzero or positive mass explicitly.

`prediction_error` derives `D=L‖zhat−z‖+ε_B R` from the actual state and operator errors. `mass_lower` derives the fitted mass lower bound; `fitted_mass_positive` proves positivity under the strict budget. `normalized_residual` proves the exact subtraction identity. The numerator estimate uses the actual vector, rather than postulating the final posterior error.

`normalized_error_checked` uses a positive checked fitted denominator. `normalized_error_margin` uses the true mass margin minus the dual-norm error budget. `filtering_step` separates the state-error coefficient and forcing term. `filtering_path` applies the existing P18 product-sum theorem to the actual true and fitted recurrences. `filtering_uniform` proves the contraction estimate with a common gain below one and bounded nonnegative forcing.

The true state and posterior radius bounds are supplied hypotheses. A checked realized fitted denominator does not establish a probability cone for every fitted operator, or validity of unchosen branches.

## P32 — exactly what was proved and what remains

`SubspaceCoordinates.lean` constructs the projection from a true subspace to an estimated subspace without choosing orthonormal bases. Given the explicit gap `‖P−Q‖≤δ<1`, it proves the lower bound `sqrt(1−δ²)‖x‖≤‖Qx‖` and injectivity. For equal-dimensional subspaces, `coordinateEquiv` constructs the continuous linear inverse, and `coordinate_inverse_bound` proves the reciprocal square-root bound.

**The gap bound is a hypothesis here. It has not been derived from `Y=X+E`.** Remaining obligations are:

1. Connect the pinned sorted-singular-value definition to the required min-max characterization and prove the perturbation inequalities, including the maximum-rank zero convention.
2. Construct/identify the leading-r left singular subspace of Y and prove its tail residual estimate.
3. Prove the equal-rank orthogonal-projection norm identity, or another valid route to the same `2ε/s` bound.
4. Connect the basis-free coordinate equivalence to `U (Uhatᵀ U)⁻¹` and the stated smallest-singular-value bound.

The pinned Mathlib file `Analysis/InnerProductSpace/SingularValues.lean` supplies the definition, nonnegativity, monotonicity and support/rank facts. It does not supply the missing perturbation chain in the form needed here. No missing link is installed as an axiom or disguised as a completed data-dependent theorem.

## Examples and rejection controls

`Block11Examples.lean` contains eight kernel-checked theorems: positive mass, zero mass at the margin boundary, negative fitted mass, rare-branch amplification for every positive parameter, exact zero-noise core recovery, exact zero-noise filtering, a singular scalar core at the gap boundary, and comparison of the two scalar error bounds. These do not constitute empirical benchmarks.

The four new isolated controls intentionally attempt false claims: positive mass at a zero fitted denominator, positivity of a negative fitted denominator, a unit absolute posterior Lipschitz bound in the rare-branch example, and a strictly positive square-root lower bound at gap one. Controls only count if rejected with genuine proof errors and no missing imports or unknown identifiers.

## Verification and reproduction

Use the pinned Lean 4.34.0-rc2 commit `6a10ac8c22beadecabdbb0919c2b50214762f91d` and Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine dependency revisions are checked. The verifier removes project caches and compiles sequentially with warnings as errors, audits every named declaration, replays each project module through LeanChecker, and checks all expected proof rejections.

From the extracted project, before generating files:

```bash
python3 scripts/verify_hashes.py
python3 scripts/build_inventory.py
python3 scripts/check_metadata.py
```

Then run, substituting the restored kit's actual absolute path:

```bash
LD_PRELOAD=/absolute/kit/compat/app_path.so python3 scripts/verify.py --kit /absolute/kit --out /absolute/run-directory
```

The compatibility preload is the supplied runtime path shim, not a proof-check bypass. This host required `.olean.server` alongside proof objects even for batch Lean. Do not omit them when restoring this kit. Imported upstream libraries are pinned, not exhaustively rebuilt/replayed by this project run. No independent referee or second prover is claimed.

## Failure history

The original source archive passed all 1,351 declared hashes. The prior runtime directory had been pruned. First invocation failed because the compiler was missing. All seven saved runtime parts reconstructed the expected combined archive hash. Full extraction exhausted disk. A reduced extraction omitted `.olean.server` files that turned out to be required; those were restored from the same saved parts. These are environment failures, not rejected mathematical propositions.

Development failures include a premature compile before its dependency, the reserved lambda token, an unmarked noncomputable real inverse, a vector argument incorrectly sent to a semiring tactic, scalar/module rewrite and inequality-orientation fixes, explicit recurrence arguments, namespace disambiguation, and warnings-as-errors. An incorrect addition-inequality application caused repeated deterministic heartbeat limits; fixing its orientation resolved the issue. Raising the heartbeat limit alone did not fix it.

One exploratory inherited run compiled and replayed its old target list but failed the final source-snapshot check because development had resumed. An attempted process interruption did not succeed. That run is not accepted release evidence. The accepted cumulative run must use a stable source inventory. The metadata command was also once invoked from the wrong directory and rerun correctly. All available compiler snapshots and diagnostics are retained.

## Continuation

Resume P32 from the exact frozen statement and the gap list above. Preserve the 38 completed propositions and the distinctions between a conditional coordinate lemma, a noisy-table theorem, and global process identification. Do not change the frozen manuscript to make coverage easier.
