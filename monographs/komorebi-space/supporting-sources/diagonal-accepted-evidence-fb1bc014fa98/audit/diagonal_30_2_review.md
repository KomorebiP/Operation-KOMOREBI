# Independent review of Theorem 30.2

**Verdict: proved as written.** The frozen Lean source matches all four conclusions of the printed theorem on the actual infinite Hilbert model. No mathematical or statement-correspondence defect was found.

This was read-only source reasoning and exact statement comparison. The reviewer inspected the recorded clean compiler and axiom results but did not run a duplicate compilation, edit source, or use numerical experiments as proof.

## Exact target and revision

The authoritative target is Theorem 30.2, label `WR11`, in `proofs/PRINTED_DIAGONAL_THEOREMS.tex`.

The frozen `DiagonalAsymptotic.lean` hash is `6d1cb7c7e068b9e007c0304359db172ee3ecd66bd90fae6a72d23076de0a0c47`. Exact hashes for the target, both newly audited files, the actual-model file, and all supporting project files are in the accompanying JSON.

On the real Hilbert space of square-summable positive-coordinate sequences, with `(Tu)_n=u_n/n` and `w_n=1/n`, the target is:

1. `A_m/m → π/4`.
2. `m B_m → π/4`.
3. `M β(T,w,M) → π/4` for **all real budgets** `M → ∞`.
4. `sqrt(N) ‖w − T hardPrefix(N)‖ → 1` at the hard-prefix correction's actual norm budget.

Natural index `j` represents printed coordinate `j+1`. All norms and infinite sums are those of the actual model, not finite-prefix substitutes.

## Proof dependencies and decisive checks

The scalar proof follows a different valid route from the printed compact-interval Riemann-sum proof. It uses two decreasing kernels, `h(x)=1/(1+x²)` and `f(x)=h(x)²`. Their half-line integrals are `π/2` and `π/4`. The latter is proved from the explicit antiderivative `(x/(1+x²)+arctan x)/2`, including its endpoint and infinite limit.

For each nonnegative decreasing integrable kernel, the source proves

`integral(k) − k(0)/m ≤ rightSum(k,m) ≤ integral(k)`.

This controls the complete infinite series with a vanishing error. The identities `A_m/m=rightSum(f,m)` and `mB_m=rightSum(h,m)−rightSum(f,m)` then give both constants `π/4`. In particular, the residual kernel's lack of monotonicity causes no gap: it is represented by a difference of two already controlled sums. Summability justifies splitting those sums.

The budget identity is for `BudgetProfile.beta`, the distance from the datum to the image of the actual closed Hilbert ball. `budget_at_sqrt_A` connects the regularized correction to this profile through the existing residual-optimality theorem. It is not a newly defined proxy for the residual.

The transfer to arbitrary budgets is explicit. The mesh `u_n=sqrt(A_(n+1))` is positive, monotone, divergent, and has consecutive ratios tending to one. A first-crossing index gives `u_n≤M<u_(n+1)` for every sufficiently large real `M`. The chosen index tends to infinity. Nonnegativity and antitonicity of the profile justify the two bounds

`u_n β(u_(n+1)) ≤ M β(M) ≤ u_(n+1) β(u_n)`.

Both outer terms tend to `π/4`, so the conclusion genuinely ranges over `M : ℝ`. Weak monotonicity of the mesh is sufficient; strict monotonicity is not silently assumed. Initial zero indices and negative budgets are excluded only through explicit eventual conditions.

The hard-prefix correction is a finite sum of unit coordinate vectors inside the same infinite Hilbert space. Its squared norm is `N`, and its residual square is exactly the omitted tail `sum_(n>N) 1/n²`. The proved integral bounds give `N/(N+1)≤N*tail≤1`. Square-root continuity supplies the comparator constant one. The source includes both a norm-budget version and the literal printed `sqrt(N)` version.

## Obligation matrix

| Obligation | Result |
|---|---|
| Actual Hilbert space, indexing, operator, datum, and norm identities | Passed |
| Exact `π/4` constants and valid infinite-sum control | Passed |
| Residual identity without a false monotonicity assumption | Passed |
| Actual budget-profile identification | Passed |
| Positive divergent ratio-one mesh | Passed |
| Arbitrary real-budget bracketing and squeeze | Passed |
| Actual hard-prefix vector, norm, and omitted tail | Passed |
| Printed four-part statement and boundary cases | Passed |
| Inspected recorded compiler/axiom evidence | Passed |

## Source and compiler checks

`DiagonalAsymptotic.lean`, `MonotoneBudgetAsymptotic.lean`, and `InfiniteDiagonalModel.lean` were read in full. Relevant supporting statements and proofs were inspected in the series, definitions, budget-profile, and regularization files. This does not claim a fresh complete audit of all earlier project modules.

The pinned local mathematical-library statements for monotone sum/integral comparison, the arctangent improper integral, the half-line fundamental theorem, and positive scaling of the half-line integral were checked against their uses. No web lookup or external novelty claim was needed.

Recorded compilation run 14 has matching before/after frozen hashes, exit code zero, `-DwarningAsError=true`, and an empty output log. Its associated axiom record includes all 47 declarations and the final bundled theorem. Every reported axiom set is contained in `propext`, `Classical.choice`, and `Quot.sound`.

The compiler/kernel and pinned dependency objects remain the formal trust boundary. This reviewer did not independently rebuild the external cache or reconcile every imported object with source. The root's planned exact-source replay and archive identity check remain the final verification steps.

## Remaining implication

No additional mathematical implication is missing from the four-part Theorem 30.2 target in this frozen source. The final `sharp_diagonal_budget_asymptotic` declaration contains all four conclusions directly, without assuming a scalar asymptotic or a sampled-budget limit as an external hypothesis.
