# Independent printed-proof audit: WR03–WR05

**Normalized claim.** Let `H` and `Y` be complete real Hilbert spaces, `T : H → Y` a bounded linear map, `r ∈ Y`, and `M ≥ 0`. Define the real number

\[
\beta_{T,r}(M)=\inf\{\|r-Ta\|:a\in H,\ \|a\|\le M\}.
\]

WR03 asserts attainment, nonincreasing and convex dependence on the nonnegative real budget, the stated operator-norm Lipschitz bound, convergence to the distance from `r` to the range closure, and the two exact finite-budget equivalences. WR04 asserts equality with an **attained maximum** over the closed unit ball in `Y`, together with strict exclusion of all residuals at most a proposed tolerance. WR05 compares two bounded linear operators on the **same normed correction space and target** and proves both the absolute profile bound and the nominal-witness lower bound.

**Primary verdict: proved as written.** This verdict covers the theorem statements and their printed proofs at the exact source hash below. It is a mathematical proof audit, not acceptance of new Lean evidence. There is no missing mathematical implication in WR03–WR05 under the stated Hilbert setting. A minor adjacent explanatory wording issue is recorded separately below; it does not affect the theorem statements or their proofs.

## Scope and source identity

The reviewer received the exact target and raw contextual sources, rather than a proposed verdict or formal implementation. The critical implications were reconstructed directly before searching historical review records. No mathematical source, Lean file, evidence label, or ledger was edited. The only written file from this audit is this report.

The base identity was checked against `budget_v1.10.0/records/BASE_CHECKPOINT.json`:

| Artifact | SHA-256 |
|---|---|
| `budget_v1.10.0/records/BASE_CHECKPOINT.json` | `01d1b8b8a925c61c7aa1e4ea2d0ce365ed175cf0d21b7ef863c9b622f810fa69` |
| Parent archive `output/Komorebi_Space_Monograph_v1.9.0.zip` | `f04fb35e1473800c604b25a1c883f6cdc937a31f9332d1ac99e8467c7a05fec9` |
| Parent formal receipt `continuation/integration/runs/wr01_wr02_overlay_01/receipt.json` | `ed08da780d623b1b53936a80207a76f63b9fd3ca02fa8f43e47ee7ca5660467b` |
| Target `budget_v1.10.0/records/TARGET_WR03_WR05.tex` | `2c82d9800d3ee58958f953888f95734b47d61f0b05030dd931ce39f51037219b` |
| Original `monograph_v1.9.0/source/chapters/05g_budget_certificates.tex` | `2c82d9800d3ee58958f953888f95734b47d61f0b05030dd931ce39f51037219b` |
| Context `05f_bounded_realization.tex` | `a18010f68701653e92ec0d25a4e2ff977244aa95fefb891ff53f26800a37402d` |
| Context `05h_regularized_repair.tex` | `9c5e9253ba9f1e0f179f60082531708cb6c00047d06bcbcb8459fc0a7534ce51` |
| Internal background `12_proof_tools.tex` | `c7b628a1ca10f37e69146b03555d2242f6c0b12f6aeae773ae3d3c8b1fdca9d0` |

All contextual chapter paths in the final three rows are relative to `monograph_v1.9.0/source/chapters/`. The parent checkpoint is `KS-v1.9.0-full-monograph-proofread`. The target snapshot and original chapter have identical bytes.

Exact target locators: definition at lines 2–6; WR03 at lines 9–57; WR04 at lines 65–111; WR05 at lines 132–176. The protected-space convention is `H = ker p`, with the inherited Hilbert norm, and `T = d|H`. The adjoint has type `T* : Y → H`, not `d* : Y → E`.

No extra assumptions of finite dimension, separability of `H` or `Y`, injectivity, surjectivity, or closed range are permitted or used. Budgets are finite real numbers; the profile theorem does not quantify over a negative or infinite budget. Convexity is on `[0,∞)`. In WR05, the tilde operator is in the same established class of bounded linear maps; this is also required to type its operator norm and adjoint.

## Dependency graph

| Dependency | Role and status |
|---|---|
| Real inner-product identities, Cauchy–Schwarz, triangle inequality, real infimum and sequence-limit properties | Foundational algebra/order/analysis leaves; used explicitly below. |
| Completeness + convex midpoint argument | Internal proof in `12_proof_tools.tex`, `lem:projection-tool`; supplies projection onto closed convex sets. Its minimizing-sequence argument is Cauchy by the parallelogram identity. |
| Closed-subspace projection → Riesz representation → bounded adjoint identity | Internal proof in `12_proof_tools.tex`, `lem:riesz-tool` and subsequent adjoint construction. No closed range of `T` is used. |
| Projection + countable span + diagonal coordinate subsequence + Bessel bound | Internal proof in `05f_bounded_realization.tex`, `lem:weak-subsequence`; supplies a weakly convergent subsequence of any bounded sequence in an arbitrary complete real Hilbert space. |
| Weak subsequence + bounded linearity + norm lower semicontinuity | WR03 attainment at the **same** budget. Lower semicontinuity can be obtained directly by pairing with a normalized nonzero limit. |
| Attainment + convex combinations / inclusion / radial rescaling | WR03 convexity, monotonicity, Lipschitz estimate. |
| Projection onto `closure(range T)` + density + attainment | WR03 floor, real-budget limit, finite-budget floor equivalence, zero-residual equivalence. |
| Adjoint identity + Cauchy–Schwarz | WR04 universal weak dual inequality and strict exclusion. This part does not depend on attainment. |
| WR03 attainment + feasible one-sided segment + Hilbert-ball support | WR04 an actual maximizing dual witness at every budget. |
| Candidate residual comparison on one common ball + real infima | WR05 absolute profile difference. Attainment is unnecessary for this part. |
| WR05 lower comparison + nominal WR04 weak dual inequality | WR05 nominal certificate. Full dual attainment is stronger than what this final step needs. |

There is no cycle: projection is proved by a Cauchy midpoint argument, not by WR03; weak sequential compactness is proved independently before WR03; WR04 uses WR03 once; WR05 can use the weak inequality from WR04 without using its maximizing-witness construction. WR06–WR09 regularization results are **not** prerequisites. In particular, proof of equality at only regularized budgets would not discharge WR04 for all budgets.

All substantive background leaves needed here have local printed arguments and are checked at that level. The contextual Clason and mathlib citations are background attribution, not an unchecked external theorem required to close this argument. No external literature claim or online source verification is needed for this audit.

## Independent derivation of the critical implications

### 1. The object minimized and attainment without ambient separability

Write `B_M = {a ∈ H : ‖a‖ ≤ M}`. It contains `0`, so the set of residual norms is nonempty, is bounded below by `0`, and contains `‖r‖`. Its infimum is therefore a finite real number with `0 ≤ β(M) ≤ ‖r‖`. By the infimum property choose `a_n ∈ B_M` with residual norm below `β(M)+1/(n+1)`. This is a minimizing sequence in the actual correction space, not in an auxiliary coordinate model.

To verify the weak compactness step independently, let `H₀` be the closed real span of the countable family `{a_n}`. Finite rational linear combinations form a countable dense subset of `H₀`. Gram–Schmidt on that dense sequence gives a finite or countable complete orthonormal family in `H₀` (and the empty family when `H₀={0}`). For every basis vector the scalar coordinate sequence is bounded. Repeated scalar subsequence selection followed by a diagonal choice gives one subsequence with all coordinates converging. The finite-coordinate Bessel inequalities pass to the limit, so the coordinate limits have sum of squares at most `M²`. Completeness constructs their vector sum `a ∈ H₀` and gives `‖a‖ ≤ M`.

Convergence of pairings against finite basis combinations extends to all of `H₀`: the pairing error on the complement is at most `2M` times its norm. Every vector of the full space decomposes into its projection to `H₀` and an orthogonal component, which pairs to zero with all `a_n` and `a`. Thus the subsequence converges weakly in all of `H`; there is no ambient separability assumption.

For any `y ∈ Y`,

\[
\langle r-Ta_{n_k},y\rangle
=\langle r,y\rangle-\langle a_{n_k},T^*y\rangle
\longrightarrow\langle r-Ta,y\rangle.
\]

Put `v=r-Ta`. If `v=0`, its norm is already at most `β(M)`. Otherwise test this convergence against `v/‖v‖`. The pairings tend to `‖v‖`, each is at most `‖r-Ta_{n_k}‖`, and those norms tend to `β(M)`. Therefore `‖v‖≤β(M)`. Since `a∈B_M`, the reverse inequality follows from the definition of the infimum. This proves attainment with the original budget bound.

Only the chosen sequence and its countable span enter this construction. No strong convergence of the `a_n`, compactness of the norm ball, closed range of `T`, or compactness of `T` is asserted.

### 2. All profile clauses

If `M₁≤M₂`, then `B_{M₁}⊆B_{M₂}`, giving `β(M₂)≤β(M₁)`. If `a₁,a₂` minimize at nonnegative budgets and `0≤t≤1`, then

\[
\|ta_1+(1-t)a_2\|\le tM_1+(1-t)M_2.
\]

Its residual is the same convex combination of the two residuals. The triangle inequality gives precisely the stated convex inequality, in the correct direction.

For `0≤M₁≤M₂` with `M₂>0`, take a minimizer `a₂` and set `a′=(M₁/M₂)a₂`. Then

\[
\|a'\|\le M_1,\qquad
\|a_2-a'\|=(1-M_1/M_2)\|a_2\|\le M_2-M_1.
\]

Consequently `β(M₁) ≤ β(M₂)+‖T‖(M₂−M₁)`. This combines with monotonicity. The only denominator is `M₂`, and the printed proof separately treats `M₂=0`, when both budgets are zero.

The closure `C=closure(range T)` is a closed linear subspace. Projection yields `b∈C` and `r-b ⟂ C`. Hence for every `a`,

\[
\|r-Ta\|^2=\|r-b\|^2+\|b-Ta\|^2=q^2+\|b-Ta\|^2.
\]

This gives `β(M)≥q`. For any tolerance `ε>0`, density gives a **single** `a_ε` with `‖b-Ta_ε‖<ε`. For all real budgets `M≥‖a_ε‖`, the triangle inequality also gives the explicit tail bound `q≤β(M)<q+ε`. This proves the full real-parameter limit at infinity, rather than only a limit along integer budgets. The printed square-root bound is equivalent and valid even when `q=0`.

If `β(M)=q`, an attained minimizer makes the nonnegative second square vanish, so `Ta=b` with `‖a‖≤M`. Conversely such a correction has residual `q`, and the floor bound forces equality. For the zero criterion there is no implicit hypothesis `q=0`: directly, `β(M)=0` and attainment give `r-Ta=0`; alternatively `0≤q≤β(M)=0` first proves `q=0` and then `b=r`. An exact feasible correction conversely gives residual zero. Thus the printed phrase “setting q=0” is a legitimate abbreviated corollary, not a restriction on the zero criterion.

### 3. The support equality and an actual maximum

For any feasible `a` and any `‖z‖≤1`,

\[
\langle r,z\rangle-M\|T^*z\|
\le\langle r-Ta,z\rangle\le\|r-Ta\|.
\]

The first inequality uses `⟨a,T*z⟩≤‖a‖‖T*z‖≤M‖T*z‖`; the second is valid even if the pairing is negative. Taking the infimum over the common, nonempty correction ball proves weak duality. If its left side is strictly greater than `ε`, every residual norm is strictly greater than `ε`, so no candidate has residual at most `ε`. No nonnegativity assumption on `ε` is needed for that implication.

Choose any attaining `a_M` and let `v=r-Ta_M`. If `v=0`, weak duality puts every dual value at most zero and `z=0` attains zero. Suppose `v≠0`, and set `z=v/‖v‖`, so `‖z‖=1`.

For every `a∈B_M` and every `0<t≤1`, the vector `a_M+t(a-a_M)` remains in `B_M`. Expanding the squared residual and dividing by the positive `t` gives

\[
2\langle v,T(a-a_M)\rangle\le t\|T(a-a_M)\|^2.
\]

Letting `t` tend to zero yields `⟨v,T(a-a_M)⟩≤0`, and dividing by `‖v‖>0` gives

\[
\langle T^*z,a\rangle\le\langle T^*z,a_M\rangle
\quad\text{for every }a\in B_M.
\]

For any `w∈H`, the support value of `B_M` is exactly `M‖w‖`. Cauchy–Schwarz gives the upper bound. When `w≠0`, the vector `Mw/‖w‖` lies in `B_M` and attains that value; this formula remains a valid zero vector when `M=0`. When `w=0`, every pairing is zero. Thus no division by `M` or by zero is needed. Taking `w=T*z` shows the pairing at `a_M` equals `M‖T*z‖`.

Substitution now gives

\[
\langle r,z\rangle-M\|T^*z\|
=\langle r-Ta_M,z\rangle=\|v\|=\beta(M).
\]

This is the required witness for a **maximum**, not merely a supremum identity. It does not rely on norm compactness of the dual ball or exchange of an infimum and supremum. Noninjectivity is harmless because the argument uses only the common residual and feasible variations.

### 4. Robustness and the common correction ball

Let `T,Ṫ : H→Y` be bounded linear maps on exactly the same Hilbert spaces and metrics. Put `c=δ+ηM≥0`. For every `a∈B_M`,

\[
\|(r-Ta)-(\widetilde r-\widetilde Ta)\|
\le\|r-\widetilde r\|+\|T-\widetilde T\|\|a\|
\le\delta+\eta M=c.
\]

The reverse triangle inequality gives both pointwise residual comparisons. To justify the infimum step without assuming coincident minimizers, choose a nominal correction with nominal residual below its infimum plus `ε`. The original profile is at most its original residual, hence below `β_{Ṫ,r̃}(M)+c+ε`. Let `ε↓0`. Interchanging the two problems gives the reverse comparison. These are equivalent to the asserted absolute-value inequality. Since the two domains are exactly `B_M`, the approximate nominal correction is admissible in the original problem.

The lower comparison says `β_{T,r}(M)≥β_{Ṫ,r̃}(M)-c`. Nominal weak duality says `β_{Ṫ,r̃}(M)≥⟨r̃,z⟩-M‖Ṫ*z‖` for every `‖z‖≤1`. Combining these inequalities proves the printed certificate with **minus** `δ` and **minus** `ηM`. No assumption relating the actual minimizers is used.

## Obligation matrix

| Obligation | Result | Decisive check |
|---|---|---|
| Exact scalar field, spaces, budget and operator typing | Passed | Complete real Hilbert `H,Y`; bounded linear `T`; `M≥0`; adjoint targets `H`. |
| Profile is a finite, nonnegative real infimum | Passed | Zero correction is feasible; residual norms bounded below by zero. |
| WR03 attained minimum | Passed | Weakly convergent bounded subsequence remains in the same ball; adjoint pairings identify the residual weak limit; norm bound realizes the infimum. |
| No separability assumption added | Passed | Only the closed span generated by the selected countable sequence is made separable. |
| Nonincreasing profile | Passed | Inclusion of correction balls, with correct order of infima. |
| Convex profile on nonnegative budgets | Passed | Feasible convex combination and residual triangle inequality; `t=0,1` included. |
| Lipschitz inequality with coefficient `‖T‖` | Passed | Radial scaling displacement ≤ budget difference; zero denominator excluded explicitly. |
| Projection floor and Pythagorean identity | Passed | `closure(range T)` is a closed linear subspace; projection error orthogonal to it. |
| Limit for all real budgets tending to infinity | Passed | Approximate preimage fixed before choosing threshold; every greater budget works. |
| Finite-budget floor iff projected datum has budgeted preimage | Passed | Uses an actual minimizer; no passage from closure to range without attainment. |
| Zero profile iff exact budgeted feasibility | Passed | Attainment gives exact equality; also forces `q=0` rather than assuming it. |
| WR04 all-witness lower inequality | Passed | Restricted adjoint, Cauchy–Schwarz and norm budget. |
| WR04 strict exclusion certificate | Passed | Dual value > tolerance implies every feasible residual > tolerance. |
| WR04 sharpness and maximum attainment | Passed | One-sided segment variation + explicitly attained support of Hilbert ball. |
| Zero residual and zero adjoint witness cases | Passed | Use `z=0` at zero residual; support value is zero if `T*z=0`. |
| Zero budget, zero operator, zero spaces | Passed | All formulas reduce to singleton/constant profile; no normalization by zero. |
| Noninjective operator | Passed | No inversion or unique correction is required. |
| WR05 two-sided profile comparison | Passed | Pointwise norm difference + infima on one common feasible ball. |
| WR05 uncertainty signs and scaling | Passed | Error is `δ+ηM`; original lower bound subtracts this quantity. |
| WR05 same correction space / same norms | Passed | Explicit in setup and printed warning; changing kernel is not covered. |
| Two-dimensional rational example | Passed | `‖a‖²=41/100`, `‖v‖²=89/100`, `T*v=a`, pairing `13/10`; normalized witness proves equality. |
| New Lean coverage / integrated compiler acceptance | Out of scope | Requires review of exact final declarations and accepted run evidence separately. |
| Global audit of WR01–WR16 or historical literature novelty | Out of scope | Only necessary local background and contextual conventions were checked. |

No theorem obligation in this matrix is conditional, failed, or unaddressed.

## Boundary and adversarial cases

1. **`M=0`.** The correction ball is `{0}`, so `β(0)=‖r‖`. The dual problem is `max_{‖z‖≤1}⟨r,z⟩=‖r‖`, attained at `r/‖r‖` when `r≠0`, or `0` otherwise. The support penalty is zero regardless of `T*z`. WR05 reduces to the reverse triangle bound `|‖r‖−‖r̃‖|≤δ`.

2. **`r=0` or a zero optimal residual.** The zero correction gives `β(M)=0` whenever `r=0`. More generally if a budgeted exact correction exists, `z=0` always attains the dual maximum. A norm-one maximizing witness need not exist: for `T=I` on `ℝ`, `r=0`, and `M>0`, every unit witness gives `−M<0`, while `z=0` gives zero. This explains why the theorem uses the unit **ball**.

3. **`‖T‖=0`.** Bounded linearity gives `T=0`; then `β(M)=‖r‖` for all budgets, `C={0}`, `b=0`, and `q=‖r‖`. Every feasible correction has the same residual; the zero correction attains the floor. The Lipschitz bound becomes equality with constant zero. Zero-dimensional `H` is included in this case. Zero-dimensional `Y` gives `r=0` and an identically zero profile.

4. **`T*z=0` with positive optimal residual.** For example, take `T(a)=(a,0)` from `ℝ` to `ℝ²`, `r=(0,1)`. Then the zero correction is optimal for every budget and `z=(0,1)` has `T*z=0`. The support equality is `0=M·0`, and the dual value is `1`. A proof that divides by `‖T*z‖` would miss this legitimate case; the printed proof does not.

5. **Noninjectivity.** With `T(x,y)=x`, `r=1`, and `M=2`, every `(1,y)` with `|y|≤√3` is an optimal correction. The best residual is uniquely zero, the least-norm correction is `(1,0)`, and correction uniqueness is false. WR03–WR05 never require it. The unique least-norm preimage exists because the preimage of the fixed optimal reachable vector is a nonempty closed affine set. Its norm is at most that of an already feasible preimage, so it remains budget-feasible.

6. **Nonclosed range / unattained unrestricted floor.** On `ℓ²`, let `T(x_n)=(x_n/n)` and `r=(1/n)`. Finite-support corrections approximate `r`, so `b=r` and `q=0`; an exact preimage would have all coordinates `1` and is not in `ℓ²`. Thus `β(M)>0` for every finite `M`, yet `β(M)→0`. This is consistent with every clause and refutes any replacement of finite-budget attainment by an unrestricted zero-infimum claim. Adding an orthogonal constant component to the target gives the same phenomenon with `q>0`.

7. **Changed correction space.** Let ambient `E=Y=ℝ`, `d=I`, and `r=1`. Under protected space `H={0}`, the profile is always `1`; under protected space `H̃=ℝ`, its value at `M=1` is `0`. The ambient map and datum are identical, so ambient error bounds `η=δ=0` would not explain this difference. The restrictions have different domains and cannot be subtracted as operators on one `H`. This is a counterexample to extending WR05 to changed kernels using only ambient operator/data errors, not a counterexample to WR05 as stated.

8. **Operator error must scale with budget.** On `ℝ`, let `T=0`, `Ṫ=ηI`, `r=r̃=ηM`, with `η,M>0`. Then `β_{T,r}(M)=ηM` and `β_{Ṫ,r̃}(M)=0`; equality holds in the operator-error part of WR05. Omitting `M` or the operator term is invalid. Taking zero operators and data `r=δ`, `r̃=0` similarly attains the data-error term.

9. **Ball-image closedness is not range closedness.** A convergent sequence `Ta_n` with `‖a_n‖≤M` has a weakly convergent subsequence of lifts with a limit still in that ball, and adjoint pairings identify its image with the norm limit. Thus every `T(B_M)` is norm closed and convex. Their increasing union need not be closed; the preceding diagonal example verifies this distinction.

These tests are exact examples and boundary reductions. They are not offered as a finite experimental substitute for the universal proofs above.

## Adjacent explanatory wording

Target line 62 says “The best residual vector is unique because it is the projection of r onto a closed convex set,” followed by a statement about its preimages. Strictly, if `K_M=T(B_M)`, the unique **reachable** vector is `c_M=P_{K_M}r`; the residual is `v_M=r-c_M`. The relevant correction preimages solve `Ta=c_M`, not `Ta=v_M`. Uniqueness of `c_M` implies uniqueness of `v_M`, and the next least-norm correction assertion is correct when read with `c_M` as the preimage target. A future editorial pass could replace that sentence with “The best reachable vector is the projection of r onto the closed convex set T(B_M), so the best residual vector is unique.” No proof uses the imprecise wording, and no source was changed here.

## Checks, evidence boundary, and remaining gap

Read-only source checks used `rg` to locate applicable instructions, target identifiers, local background proofs, historical statuses, and known related review entries; `cat`, `sed`, and `nl -ba` to inspect the actual statements and proof steps; and Python `hashlib.sha256` / `sha256sum` to verify identities. No applicable `AGENTS.md` or `.mathbox` ledger was found in this task tree. The base record explicitly retains the existing prose/JSON ledger rather than migrating it. Historical review hits were used only to check for previously recorded scope problems, not as proof evidence.

The pinned dependency manifest identifies mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, but this audit does not claim to have checked new Lean declarations against it. Nor does the verified hash of the parent receipt constitute a rerun of its compiler commands. At this checkpoint the inherited written-status file correctly distinguishes the printed WR03–WR05 proofs from complete new formal counterparts.

**Exact remaining mathematical gap: none for WR03–WR05 at the audited target hash.** The strongest safe statement is the full normalized claim above under complete real Hilbert hypotheses. The cheapest next required check for formal completion is a clause-by-clause comparison with the exact final Lean theorem types and a fresh audit of their source at fixed hashes, followed by the project's accepted integration/axiom checks. In particular that comparison must include all real nonnegative budgets, actual infimum attainment, convexity, the zero-budget Lipschitz case, the real-parameter limit, both iff statements, an attained dual maximum, strict exclusion, and both WR05 conclusions on one fixed correction space.
