# Independent audit of the strong projection route

**Normalized claim.** In a complete real inner-product space, minimum-norm points of nested nonempty closed convex sets converge strongly whenever their norms have a uniform finite bound. Applied to a fixed norm ball intersected with shrinking residual sublevel sets, this yields the full written WR01 and WR03 conclusions. For affine sets, orthogonality strengthens the projection inequality to all the exact WR02 identities.

**Primary verdict: proved as written.** The alternative written route preserves the hypotheses and conclusions of WR01–WR03. No mathematical gap was found. This verdict concerns the written route. It does not claim that WR03, or the entire route, has been compiled in Lean.

Audit date: 12 October 2026. Separate-subagent review of the raw derivation and the authoritative monograph statements. No proof or inherited package file was edited.

## Authoritative artifacts and evidence scope

| Artifact | SHA-256 |
|---|---|
| `continuation/proofs/STRONG_PROJECTION_ROUTE.md` | `c3ca4d5d6fac5385a2753cbef1ae12350d5f951c28c315f0cf4c99498fa485c2` |
| inherited `source/chapters/05f_bounded_realization.tex` | `ba8225a03190d4040260eeced4b4c9372d05b85266b27ce53f8cc7ff9ca56acf` |
| inherited `source/chapters/05g_budget_certificates.tex` | `2c82d9800d3ee58958f953888f95734b47d61f0b05030dd931ce39f51037219b` |
| inherited `source/chapters/12_proof_tools.tex` | `f98d41969e3048a63a3ed7e19a0e7181ffb309a835ff6cb303a9ced6c5f748bd` |
| `continuation/formal/KomorebiSpace/BoundedApproximateRealization.lean` | `28ba39ebab91c4388f70c6bf746d53082f1eab5049bd7b81e0fc24d2e58cc3af` |
| `continuation/formal/KomorebiSpace/NestedMinimumCorrections.lean` | `36f748414984bd4fd6c78738a928436412ec49d7cbbb7effd8ed203bb56576c1` |
| `continuation/formal/KomorebiSpace/ProtectedBoundedRealization.lean` | `2f7a73fabdc5953e378f77e8a102089c0d43c19f8d1b3ca66e9e2250794a9ab2` |

The mathematical claim scope is Sections 1–10 of the route. Section 11 is checked below only as its stated conditional observation for WR08. The earlier report `WR01_WR02_AUDIT.md` audits the inherited weak-subsequence route independently.

The actual WR01 Lean proof uses Banach–Alaoglu and Riesz representation. The alternative written projection proof does not change that fact. Matching theorem conclusions does not establish that a particular printed proof or its every background lemma was formalized.

## Exact hypotheses and dependency graph

All spaces are real Hilbert spaces, hence complete. T is a fixed bounded real linear map. Budgets are finite real M ≥ 0. Every nested family is indexed by ℕ, every member is explicitly nonempty, closed, and convex, and nesting means Cₘ ⊆ Cₙ for n ≤ m. The affine specialization retains that additional structure. No finite-dimensionality, separability, closed-range, or norm-compactness assumption is introduced.

The dependencies are acyclic:

1. Internal Hilbert projection lemma → minimum points and the variational inequality.
2. Variational inequality + norm expansion → difference-of-energies upper bound on squared distance.
3. Nested membership + bounded scalar supremum + completeness → strong convergence of the auxiliary minimum sequence.
4. Closedness + eventual membership → a point in the entire intersection.
5. Shrinking residual thresholds + the same norm ball → exact fixed-budget WR01 and fixed-budget WR03 attainment.
6. Affine two-sided directions → WR02 equalities.
7. Attainment, convex combinations, radial rescaling, and projection onto the closed range closure → all remaining WR03 profile clauses.

The projection lemma is internally proved in the inherited appendix by a Cauchy minimizing sequence and the parallelogram law. This audit checked that argument in the preceding WR01/WR02 review. The remaining leaves are elementary real infimum/supremum properties, continuity of bounded linear maps and norms, and inner-product norm expansion. No external source is being used as an unchecked substitute for a proof step.

## Decisive reconstruction

For a minimum point p of a convex C, projection of zero gives ⟨p,x−p⟩ ≥ 0 for x ∈ C. Therefore

    ‖x−p‖² ≤ ‖x‖² − ‖p‖².

This sign is correct. With x = pₘ ∈ Cₙ, it gives the nested energy inequality, while minimality separately gives monotonicity of ‖pₙ‖. Let L be the finite supremum of the squared norms. For ε > 0 choose N with L−‖p_N‖² < ε². For any m,n ≥ N, exchange their order if needed. The inequality gives ‖pₘ−pₙ‖² < ε², hence the full sequence is Cauchy. This controls arbitrary late pairs, not only adjacent differences. Completeness and each fixed set's closedness give the common limit.

For WR01 the constraint sets are

    Cₙ = {a : ‖a‖ ≤ M and ‖Ta−r‖ ≤ 1/(n+1)}.

Each is nonempty by residual convergence of the supplied bounded sequence, independently for each n. Continuity proves closedness, linearity and the triangle inequality prove convexity, and the thresholds prove nesting. The projection sequence stays in the same ball. Its common limit has residual bounded by every positive threshold and hence zero. This constructs a new strong sequence of minimizers, without claiming that the supplied approximate sequence converges strongly or contains those minimizers as a subsequence.

For WR03 put β = inf{‖r−Ta‖ : ‖a‖ ≤ M}. The set of residual norms is nonempty, because zero is feasible, and bounded below by zero. For every δ > 0 there is a feasible point with residual < β+δ. Thus replacing the residual threshold above by β+1/(n+1) again gives nonempty nested closed convex sets. The common limit has norm ≤ M and residual ≤ β. The defining lower-bound property of β gives the reverse inequality. No assumed closedness of T's range or image of the ball occurs in this argument.

For affine sets, both p+h and p−h are feasible. The projection inequality with both directions gives ⟨p,h⟩ = 0. This yields the finite WR02 equality, and gives the limiting equality directly because the limit belongs to each affine set. No continuity passage is even needed for that final equality, although one would also be valid.

## Obligation matrix

| Obligation | Status | Finding |
|---|---|---|
| Projection inequality sign | Passed | The projected point is zero, so ⟨−p,x−p⟩ ≤ 0 means ⟨p,x−p⟩ ≥ 0. |
| Nonempty constraint sets | Passed | Proved individually from an approximate sequence or an infimum approximation. |
| Closedness and convexity | Passed | Both constraints are continuous convex norm sublevel sets of affine maps. |
| Infinite intersection from a bounded minimum sequence | Passed | Full Cauchy estimate, completeness, and fixed-set tail membership are all present. |
| Minimum-norm limit and uniqueness | Passed | Finite minimum inequalities pass to the norm limit; the intersection is closed convex. |
| Empty intersection means divergence to infinity | Passed | Unboundedness is upgraded using nondecreasing norms. |
| WR01 exact same budget | Passed | The closed ball at the original M is included at every stage. |
| WR01 equivalence and escape corollary | Passed | Constant-sequence direction and bounded-subsequence contradiction are explicit. |
| WR02 affine equalities | Passed | Convex inequality is not mislabeled as equality; both affine directions are used. |
| WR03 infimum is a finite real number | Passed | Nonempty residual set with lower bound zero and upper candidate ‖r‖. |
| WR03 attainment | Passed | Nested thresholds yield an actual attaining correction in the ball. |
| WR03 nonincreasing and convex profile | Passed | Inclusion of balls and feasible convex combinations give the stated directions. |
| WR03 Lipschitz bound | Passed | Radial rescaling controls correction displacement by M₂−M₁; M₂=0 treated separately. |
| WR03 real-budget limit | Passed | Approximate preimage is chosen first, then a budget threshold works for every larger real budget. |
| WR03 finite-budget floor equivalence | Passed | Attainment and Pythagorean residual decomposition force Ta=b. |
| WR03 zero-residual equivalence | Passed | Proved directly, without silently presupposing the residual floor is zero. |
| Closedness of each budget-ball image | Passed | Bounded lifts plus WR01 give sequential closedness in the norm metric. |
| Image versus preimage uniqueness | Passed | Unique projected image, unique least-norm preimage, potentially many other preimages. |
| Weak-subsequence background automatically formalized | Out of scope | Neither the route nor the actual WR01 formal proof establishes that printed lemma as a new named formal result. |
| New WR03 Lean coverage | Not addressed | This route is a written proof and no WR03 compiler evidence was supplied to this audit. |
| Whole-library compilation | Not addressed | Owned by the cumulative verifier, not this mathematical review. |

## Edge cases and counterchecks

- M=0 gives the singleton ball {0}; WR01 forces r=0, while WR03 gives β(0)=‖r‖.
- Zero-dimensional source or target is handled without dividing by a norm or assuming a nonzero vector.
- T=0 gives a constant profile with Lipschitz constant zero.
- Zero minimum norm and zero supremum energy cause no denominator or strictness issue.
- Convexity alone does not yield the affine equalities: [1,∞) ⊇ [2,∞) gives squared distance 1 and energy difference 3.
- Completeness remains indispensable: bounded nested finite-coordinate corrections in c₀₀ can lack any common point in c₀₀. The proof correctly uses a Hilbert space, not merely a pre-Hilbert space.
- A countable increasing union of the closed budget-ball images need not be closed. The route explicitly avoids that inference.

## Conditional WR08 observation

Section 11 is valid with precisely its stated inputs: α>0, the already constructed regularized solution aα satisfying the normal equation, the attained projected datum b=Ta*, and a* the minimum-norm preimage of b. Pairing

    T*(r−Taα) = α aα

with a*−aα gives

    α⟨aα,a*−aα⟩ = ⟨r−Taα,b−Taα⟩ = ‖b−Taα‖²,

because r−b is perpendicular to the range closure. The inner product is therefore nonnegative, giving the displayed energy inequality. With the separate image-convergence premise Taα→b, failure of norm convergence would yield a fixed smaller norm budget on a parameter sequence αⱼ→0. WR01 then contradicts minimum-norm selection of a*. The zero minimum-norm case is treated separately and correctly.

This observation does not prove its image-convergence premise, the unattained case, the positive-floor classification, or the full WR08 parameter theorem. It must not be counted as full WR08 coverage.

## Actual WR01 Lean type audit

The source hash in the artifact table was read directly. The development receipt `continuation/development/wr01/verification.json` reports `PASS`, exit code 0, for that same hash and an audit-file check. This reviewer inspected the receipt and source but did not rerun that compilation.

All declarations are in `KomorebiSpace.BoundedApproximateRealization`.

| Printed clause | Actual declaration | Match |
|---|---|---|
| Same-budget existence from image convergence | `exists_solution_of_bounded_approximation` | Exact complete-real-Hilbert scope and bound M. |
| Same-budget existence in the printed residual norm form | `exists_solution_of_bounded_residual_tendsto_zero` | Exact. |
| Range membership iff bounded approximate sequence | `mem_range_iff_bounded_approximation` | Exact, using an explicit existential real bound. |
| Every approximating sequence for an unattained datum escapes | `norm_tendsto_atTop_of_not_mem_range` | Full `atTop` divergence, not just unboundedness. |
| Stronger frequent-budget helper | `exists_solution_of_frequently_bounded` | General nontrivial-filter statement, with explicit `NeBot` and a frequently recurring budget. |

No theorem assumes closed range, finite dimension, separability, existence of an exact solution, or the conclusion itself. The frequent-budget helper extracts a weak-dual cluster point and transports it through the Riesz equivalence; evaluation convergence identifies its image. Its conclusion retains the same budget. This differs from both the printed weak-subsequence proof and the optional strong projection proof, but establishes the same WR01 principal mathematical conclusions.

## Actual WR02 Lean type audit

The final source identity in the artifact table was read directly and matched `continuation/development/wr02/WR02_COMPILE_RECEIPT.json`. The persisted receipt records accepted `compile03` exit code 0 with warnings treated as errors, followed by a zero-exit axiom export for all 19 explicit declarations. The exported lists contain only `propext`, `Classical.choice`, and `Quot.sound`. The receipt also records four passing positive examples and both expected negative rejections. This reviewer inspected the receipt and axiom log but did not rerun those checks. All declarations below are in `KomorebiSpace.NestedMinimumCorrections`.

| Printed clause | Actual declaration or construction | Match |
|---|---|---|
| Existence of each least-norm point | `exists_minimum`, `minimumPoint`, `minimumPoint_spec` | Constructed from nonempty, closed, convex sets, rather than assumed as data. |
| Uniqueness | `minimum_unique` | Global minimum-norm property and convexity suffice. |
| Canonical affine minimum sequence | `affineCorrections`, `affineCorrections_spec` | Arbitrary nonempty closed affine family. |
| Finite exact energy equality | `nested_affine_energy` | All n ≤ m, same equality as WR02. |
| Nondecreasing minimum norms | `nested_affine_norm_monotone` | Exact. |
| Intersection nonempty iff bounded minimum norms | `nested_affine_intersection_iff_bounded` | Explicit existential finite real bound, avoiding an ill-typed real infinity. |
| Norm convergence to a least-norm point in the entire intersection | `nested_affine_strong_realization` | Norm-topology `Tendsto` and actual intersection membership inside `IsMinimum`. |
| Uniqueness of that intersection minimum | `nested_affine_strong_realization` | Explicit universal uniqueness conjunct. |
| Limiting exact energy identity for every n | `nested_affine_strong_realization` | Explicit final conjunct, derived by affine geometry. |
| Empty-intersection norm divergence | `nested_affine_escape` | Full `Tendsto ... atTop atTop`. |

The helper `exists_mem_iInter_of_closed_convex_bounded` is stronger than the affine existence implication, while `minimum_energy_le` gives only the appropriate inequality for general convex sets. The affine equality is established separately using both feasible directions. Thus no convex-only result is being passed off as the full affine theorem.

The `IsMinimum` definition includes membership and comparison with every element of the actual set. The chosen minimum sequence does not assume an intersection point or a convergence conclusion. The public affine theorems retain complete-real-Hilbert hypotheses. A few purely geometric/algebraic helpers correctly omit unused completeness assumptions; this does not weaken the final claims' needed hypotheses.

## Actual protected-kernel bridge audit

The final bridge hash in the artifact table matches `continuation/development/protected02/bridge_verification.json`, which records exit code 0. The reviewer read that receipt and the final proof directly but did not rerun the compilation.

The public declaration is `KomorebiSpace.ProtectedBoundedRealization.exists_exact_repair_of_bounded_approximation`. For bounded continuous linear D and p, a raw f, a sequence uₙ in the actual subtype `p.ker`, and a bound M, it assumes `‖uₙ‖ ≤ M` and `‖D(uₙ)−D f‖ → 0`. Its conclusion is

    ∃ y : E, D y = 0 ∧ p y = p f ∧ ‖f−y‖ ≤ M.

This is exactly the requested ambient repair conclusion with the same original budget and protected value. The proof applies WR01 to the actual restricted operator on the complete kernel, obtains a with D a = D f, and sets y = f−a. The kernel membership proves p a = 0. The final norm rewrite identifies f−y with a and uses the inherited subtype norm. No ambient-coordinate norm surrogate or altered budget enters.

The codomain of p is allowed to be a normed real space, which is a harmless generalization of the monograph's Hilbert codomain. Completeness of the kernel comes from closedness of the continuous map's kernel in the complete ambient space. No closed-range assumption is introduced.

Two earlier bridge attempts failed, first because a required inherited dependency was absent from the scratch build closure and then because a subtype-norm simplification did not close the goal. The final direct rewrite and exact inherited norm proof resolve the latter without changing the theorem type. These are development failures, not accepted verification evidence.

## Remaining gap and cheapest next check

No mathematical gap remains in the reviewed alternate written WR01–WR03 route. WR03 remains a written result until every printed clause has actual formal counterparts and accepted compiler evidence. The WR01, WR02, and protected bridge public source types match their claimed scope at the hashes above. The accepted cumulative verification receipt remains a separate evidence obligation, and this audit does not substitute for it.

If the alternate proof is incorporated into the monograph later, synchronize the WR01 and WR03 proof descriptions, the background-dependency appendix, and WR08's reference to the old adjoint pairing argument. The route identifies these dependencies correctly. No inherited source synchronization was performed by this audit.
