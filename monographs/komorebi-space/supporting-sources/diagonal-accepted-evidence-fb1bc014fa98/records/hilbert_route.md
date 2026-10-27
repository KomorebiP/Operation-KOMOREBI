# Infinite Hilbert diagonal model route

Base checkpoint `diagonal-formalization-base-01`, parent SHA-256
`67e308826abe33873e1d99d6fcf70bb14df65d6b511597b295b0bf430520a990`.

This file records an in-progress construction, not a verified theorem claim.

## Planned exact objects

- `H := lp (fun _ : ℕ => ℝ) 2`, using mathlib's complete real inner product structure.
- `T` multiplies coordinate `j` by `(index j)⁻¹` where `index j = j+1`.
- `w,a m,v m,b,c m` realize the five shared scalar coordinate families.
- `alpha m := ((m : ℝ)^2)⁻¹`, positive for `m ≥ 1`.

## Obligations

1. Establish actual square summability (dependency on `DiagonalSeriesBounds`).
2. Construct the bounded linear multiplier using the uniform bound `|(index j)⁻¹| ≤ 1`.
3. Show self-adjointness from the actual l2 inner product sum, not an assumed diagonal axiom.
4. Prove the normal equation coordinatewise and use `RegularizedHilbertRepair.normal_unique`.
5. Identify the residual vector and exact squared norms with the infinite sums `A,B`.
6. Identify the attainable datum `b = T w`, prove injectivity and thus minimum norm of `w`.
7. Prove the attainable correction `c` and its bias vector `w-c=v`.

No Lean compilation has yet run: pinned environment is being provisioned by the parent agent.

## Source inspection update

The exact pinned mathlib checkout is available at `.lean_runtime/mathlib` in the scratch workspace. Inspected `Analysis/Normed/Lp/lpSpace.lean` and `Analysis/InnerProductSpace/l2Space.lean`. Construction uses `Memℓp.mono'`, `lp.norm_mono`, and the exact theorem `lp.inner_eq_tsum`.

The first uncompiled draft is now `lean/KomorebiSpace/InfiniteDiagonalModel.lean`. It additionally identifies the actual budget profile at `sqrt (A m)` through `BudgetProfile.exists_budget_minimizer` and `RegularizedHilbertRepair.residual_best_at_budget`. This is only the profile identification part of Theorem 30.2, not its asymptotics.

## Independent static review

A read-only child review checked exact semantic correspondence and the pinned API signatures. It found no definite error, but its verdict is conditional on compilation. It confirmed that the norm/profile identification concerns the actual infinite `lp` space. The full series inequalities, noisy rounded-rate application, and asymptotics remain separate dependencies; this model file does not itself complete the three printed target groups.

## Pinned compilation and axiom audit: completed model module

`InfiniteDiagonalModel.lean` compiled with Lean 4.34.0-rc2, pinned mathlib, `-j1 -DwarningAsError=true -DautoImplicit=false`, emitting its project olean. The first full attempt (`logs/hilbert_compile_002_full.log`) found only two tactic-linter errors. Removing a redundant `ring` and an unnecessary `<;>` fixed them. `logs/hilbert_compile_003_full.log` is the clean core pass (exit 0).

The assigned hard-prefix extension was then added and compiled cleanly on its first full attempt; `logs/hilbert_compile_004_prefix_extension.log` records exit 0 with no diagnostics. The module proves `norm_hardPrefix_sq` and `norm_hardPrefix_residual_sq` in the same actual infinite space. It also exposes square summability of the attainable coordinate families.

The 48 public declarations are inventoried with the final source SHA-256 in `records/hilbert_inventory.json`. `logs/hilbert_axiom_audit.lean` imports the compiled module and prints each declaration's transitive axioms. The audit exited 0; every declaration depends only on `propext`, `Classical.choice`, and `Quot.sound`. No admitted proof, new project axiom, unsafe declaration, or finite substitute was introduced.

This completes this module's construction and exact-identity obligations. Proposition 30.1 additionally uses the independently compiled series bounds; Corollary 30.3 additionally requires the noisy ceiling application; Theorem 30.2 additionally requires the scalar and full-real-budget limit proofs. The latter are not asserted by this module.
