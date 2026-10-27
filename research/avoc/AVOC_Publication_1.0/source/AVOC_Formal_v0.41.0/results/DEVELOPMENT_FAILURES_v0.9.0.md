# AVOC v0.9.0 development failures and repairs

These are development-time failures, not final theorem failures.

1. **Fresh v0.9 workspace lacked inherited project `.olean` files.** Direct checking of a new module initially failed at `import AVOC...`.  For incremental development, the already clean-verified v0.8 project build artifacts were copied into the new workspace; the final v0.9 evidence does not rely on that shortcut because a full `lake clean` + aggregate rebuild was performed afterward.
2. **`Mathlib.Tactic.FieldSimp` was not present in the portable cache.** The exact pinned module was built inside the same mathlib revision.  No toolchain or revision changed.
3. **First normalization proof used unavailable/incorrect finite-sum rewrites.** `Finset.sum_div` was not available in the intended form and direct `Finset.sum_mul.symm` was ill-typed.  The proof was repaired by rewriting division as multiplication by inverses and using explicit `Finset.sum_mul` identities.
4. **Absolute-value division support required the correct ordered-field import.** `abs_div` was initially unknown.  The minimal `Mathlib.Algebra.Order.Field.Basic` dependency was added.
5. **An unused nonnegativity parameter triggered warning-as-error.** The generic normalization theorem did not require pointwise nonnegativity of the first row once its mass and L1 hypotheses were stated; the binder was marked intentionally unused rather than weakening lint settings.
6. **First prior-perturbation proof tried to infer likelihood-envelope nonnegativity indirectly from inhabitation.** This introduced ordering/declaration complications.  The theorem was strengthened semantically by requiring the natural explicit premise `0 ≤ K`.
7. **Direct rewriting inside `conditionByWeight` examples failed because proof fields depend on the evidence normalizer.** The rare-evidence posterior witnesses were proved instead from the kernel-checked pointwise conditioning identity followed by cancellation of the nonzero evidence mass.
8. **The first no-global-Lipschitz arithmetic route used an inapplicable multiplication monotonicity instance.** It was replaced by the ordered-field theorem `div_lt_one` and a `div_eq_mul_inv` normalization.
9. **The exact-zero rate-distortion corollary simplified its positivity goal farther than expected.** After `simp`, the remaining goal was `V s - V t ≠ 0`, so the proof was repaired with `sub_ne_zero.mpr` rather than an extra `abs_pos` layer.
10. **Clean build host execution cap.** As in earlier releases, the full pinned dependency graph exceeds one host execution window.  The build was resumed in non-overlapping bounded slices and eventually reported all 1066 jobs successful.  No AVOC theorem error occurred in the clean rebuild.
