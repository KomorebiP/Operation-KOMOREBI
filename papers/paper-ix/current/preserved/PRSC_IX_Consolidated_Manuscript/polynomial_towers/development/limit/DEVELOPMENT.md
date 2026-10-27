# Compatible integer towers and p-adic limits

Author: Komorebi P.

The source `PadicTowerLimit.lean` proves six declarations over the pinned Lean 4.34.0-rc2 and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06 toolchain. All local runs use the project's low-memory runner with one thread, a 240-second timeout, and `warningAsError=true`.

For a prime p, a natural starting precision L, and an integer sequence z, the only compatibility assumption is p^(L+n) divides z(n+1)-z(n) at every n. There is no assumed convergence. The proof first telescopes divisibility across any two indices, then verifies the epsilon definition of a Cauchy sequence in the actual p-adic metric. Completeness supplies a limit. Passing the eventual norm bounds to that limit retains every prescribed residue. A coordinatewise theorem gives convergence in the product topology for any coordinate type. A separate theorem shows that integer values divisible by p^(L+n) converge to zero.

The uniqueness theorem refers to limits of the same chosen sequence. It does not assert uniqueness of polynomial roots from a merely surjective rectangular Jacobian. The retained divisibility bound is not an exact valuation claim.

## Development record

- `compile_01.log`: initial check failed at two telescoping rewrites. A `convert ... using 1` left a proposition-level divisibility equality that `ring` could not normalize directly. Replaced those with explicit integer sum/difference identities and rewrites.
- `compile_02.log`: the scalar divisibility, Cauchy, and limit theorems passed.
- `compile_03.log`: added vector convergence, precision-to-zero convergence, and uniqueness of the sequence limit. Passed.
- `compile_04.log`: renamed the vanishing theorem to the parent-agreed API `divisible_int_tendsto_zero`. Passed. This is the frozen deliverable source.
- `audit_01.log`: exact scalar, vector, and vanishing statement examples passed. All six explicit declaration axiom closures were checked. Only `propext`, `Classical.choice`, and `Quot.sound` occur. The elementary integer telescoping theorem depends only on `propext`.

All failed development output is retained. No sorry, admit, native_decide, unsafe declarations, custom axioms, or unbounded heartbeats are used.
