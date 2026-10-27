# Independent formal-statement audit: complete WR03–WR05 block

**Normalized claim.** For arbitrary complete real Hilbert spaces `H` and `Y`, a bounded linear `T : H → Y`, datum `r ∈ Y`, and each nonnegative real budget `M`, the formal profile must be the printed infimum over the actual correction ball. The public results must prove every attainment, shape, limit, and equivalence clause of WR03, the attained dual maximum and strict exclusion in WR04, and both the absolute profile comparison and nominal certificate in WR05 on one fixed correction space.

**Primary verdict: proved as written.** At the frozen source hashes below, the public formal statements provide **full coverage of WR03, full coverage of WR04, and full coverage of WR05**. No clause is only partial. No missing implication, extra closed-range/finite-dimensional/separability assumption, hidden positivity restriction, changed correction norm, or surrogate-profile defect was found. The four exact sources were independently compiled in dependency order, and all 43 public declarations were independently inspected through exported elaborated types and axiom closures.

This verdict concerns mathematical source correctness and exact statement correspondence. It does not replace the project's separate cumulative integration acceptance, control suite, or publication synchronization. The adjacent reachable-vector/residual-vector prose erratum in the printed-proof audit remains a separate editorial matter and is not a defect in these theorem statements.

## Frozen artifacts and independent method

All paths in the following table are relative to `budget_v1.10.0/` unless otherwise indicated.

| Artifact | SHA-256 |
|---|---|
| `records/TARGET_WR03_WR05.tex` | `2c82d9800d3ee58958f953888f95734b47d61f0b05030dd931ce39f51037219b` |
| `formal/KomorebiSpace/BudgetProfile.lean` | `a11931c108e046080539e346bbf910a99395da0ee51dc8634f8101bb9c95170f` |
| `formal/KomorebiSpace/BudgetProfileGeometry.lean` | `edee3c011c62ef35c044fa5fe415a493ab6c0ff960970e7d7af72a71113757c6` |
| `formal/KomorebiSpace/BudgetDuality.lean` | `c79f643994957cd05b067da3a5f52e8530d1e2d332f72a7ddeb8486273d834ce` |
| `formal/KomorebiSpace/BudgetRobustness.lean` | `1406ffe483fc4de9b5688abea8e84ea2d3b5e48ba4f41127afc230a34c87e87e` |
| Accepted parent `continuation/integration/runs/wr01_wr02_overlay_01/source/KomorebiSpace/BoundedApproximateRealization.lean` | `28ba39ebab91c4388f70c6bf746d53082f1eab5049bd7b81e0fc24d2e58cc3af` |
| Accepted parent receipt `continuation/integration/runs/wr01_wr02_overlay_01/receipt.json` | `ed08da780d623b1b53936a80207a76f63b9fd3ca02fa8f43e47ee7ca5660467b` |

The final two paths are relative to the workspace root. The target identity and frozen printed background remain those recorded in `WR03_WR05_PRINTED_PROOF_AUDIT.md`.

The auditor read all four sources in full and constructed the clause mapping below independently of the authors' correspondence tables. Source declarations were not inferred from comments, theorem names, or build success alone. A temporary audit tree contained byte-identical snapshots of the four final sources; accepted parent objects were reused through links, and every new module was freshly compiled into that isolated tree in this order:

1. `BudgetProfile`
2. `BudgetProfileGeometry`
3. `BudgetDuality`
4. `BudgetRobustness`

All four compilations returned exit code `0` with `-j1 -DwarningAsError=true -DautoImplicit=false` and empty compiler logs. The successful logs all have SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. No final mathematical source was modified. The pinned Lean executable was `runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2/toolchain/bin/lean`; the existing compatibility preload was used.

An auditor-generated file imported the four fresh modules and issued `#check @NAME` and `#print axioms NAME` for all **43** named public declarations: 39 theorems, 3 definitions, and 1 instance. Its source SHA-256 is `7386a22f841b1daa108cf801043a4af004f7d72dfa0caec7e6d43119a47a5954`. The successful complete export log has SHA-256 `d0cfa06343155bd1ec31caacdf02336fc532bbccd09dc38be1b814a8901567cd`, returned exit code `0`, and is reproduced verbatim in the appendix below. The export shows the full implicit/typeclass binders, including those omitted from selected source sections.

The local mathlib checkout was independently checked with `git rev-parse HEAD` and `git diff --exit-code HEAD --`: revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, clean tracked source. Every exported declaration's axiom closure is exactly within `{Classical.choice, propext, Quot.sound}`. There is no `sorryAx` or custom axiom in these closures. A direct source scan also found no `sorry`, `admit`, `axiom`, or `unsafe` declaration.

Two preliminary audit-harness issues were corrected before the successful audit run: Lean's project namespace search required the accepted parent objects to be present in the same temporary import root, and the exporter option is `format.width`, not `pp.width`. These were harness configuration failures, not failures of the frozen mathematical sources. The successful compilation and export results above are the evidence used for the verdict.

## Definitions and hidden-hypothesis checks

### The profile is the actual infimum

`BudgetProfile.beta T r M` is defined as

```lean
Metric.infDist r (T '' Metric.closedBall 0 M)
```

`Metric.closedBall 0 M` means exactly `‖a‖ ≤ M`. The image is taken under the supplied `T`, and the distance is measured using the supplied norm on `Y`. It is neither a regularized profile, a coordinate-norm ball, a sampled candidate set, nor the closure of the unlimited operator range.

The crucial bridge is a proved public statement, not an informal interpretation:

```lean
beta_eq_iInf (T : H →L[ℝ] Y) (r : Y) {M : ℝ} (hM : 0 ≤ M) :
  beta T r M = ⨅ a : {a : H // ‖a‖ ≤ M}, ‖r - T a‖
```

Its indexed family is precisely the subtype of budget-feasible corrections. The source establishes that subtype's nonemptiness by zero and explicitly supplies a lower bound of zero when using real conditional-infimum lemmas. Thus the use of Lean's real `iInf` does not rely on an empty-family convention or on unjustified boundedness. The proof derives one side from every candidate and the other from an actual minimizer.

The definition is total on all real `M`; for a negative budget its ball is empty and `Metric.infDist` has the conventional value zero. This does **not** affect the correspondence: every printed finite-budget profile claim has nonnegative-budget scope, and every corresponding formal public statement includes that scope where needed. The limit at `atTop` depends only on an eventually nonnegative tail.

### Hilbert spaces and operator class

The complete type exports contain only the expected structural hypotheses:

```lean
{H : Type u} {Y : Type v}
[NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
[NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
(T : H →L[ℝ] Y)
```

Some lemmas require less, as documented below. The normed and inner-product structures are connected by the `InnerProductSpace` class; a separate incompatible energy norm is not introduced. Universes for `H` and `Y` are independent. No result requires finite dimension, separability, nontriviality, injectivity, surjectivity, a closed range, a coercive lower bound, a supplied minimizer, or a pre-existing maximizing dual witness as an extra assumption on its final public theorem.

The helper `exists_sharp_witness_of_variational` does assume an admissible `a` and a variational inequality, but the final `exists_attaining_dual_witness` and `sharp_budget_duality` discharge those assumptions internally. Similarly, `radial_shrink_bounds` assumes `M₂>0`, but both public Lipschitz statements split off the zero-budget case and have only `0≤M₁≤M₂`.

### The projected datum and residual floor

`rangeClosure T` is `T.range.topologicalClosure`, and `rangeClosure_coe` identifies its underlying set with `closure (Set.range T)`. `projectedDatum T r` is the orthogonal `starProjection` onto that closed submodule. Its completeness instance is derived from closedness of the closure and completeness of `Y`; it is not a user-supplied assumption that the original range is closed.

The norm-square decomposition uses `r - projectedDatum T r` and `projectedDatum T r - T a` in the stated order and proves their orthogonality. `projected_residual_eq_infDist` identifies the norm of the orthogonal residual with the distance to the range closure. Therefore the formal right-hand side `‖r - projectedDatum T r‖` is exactly the printed `q`, not a potentially different distance or a correction norm.

### Adjoint and common-domain checks

Every dual value uses `T.adjoint z`, where `T : H →L[ℝ] Y`; the adjoint therefore lands in `H` with its declared Hilbert metric. For a protected instantiation `H=ker p`, it is the restricted adjoint required by the text. The proof does not substitute an ambient `d.adjoint`.

WR05 quantifies `(T S : H →L[ℝ] Y)` and `(r s : Y)` once, so source, target, metrics, and feasible correction ball are identical in both profiles. Its operator difference is the actual operator norm `‖T-S‖`. Explicit assumptions `η≥0` and `δ≥0` are omitted in the final declarations only because `‖T-S‖≤η` and `‖r-s‖≤δ` already imply them. This is a logically redundant-hypothesis removal, not a weakening of the uncertainty bounds or an additional restriction. The source explicitly derives `η≥0` when scaling the budget inequality.

## Clause-by-clause correspondence

The table abbreviates namespaces `KomorebiSpace.BudgetProfile` as `P`, `KomorebiSpace.BudgetProfileGeometry` as `G`, `KomorebiSpace.BudgetDuality` as `D`, and `KomorebiSpace.BudgetRobustness` as `R`. Each row was checked against the actual full type, with the expected real Hilbert structural hypotheses above.

| Raw target clause | Final public theorem(s) | Quantifier and conclusion check | Coverage |
|---|---|---|---|
| Definition before WR03: infimum over `‖a‖≤M` | `P.beta`, `P.beta_eq_iInf` | All bounded linear `T`, all `r`, every real `M≥0`; exact feasible subtype and residual norm. | Full |
| WR03: attainment for every finite nonnegative budget | `P.exists_budget_minimizer` | `0≤M → ∃a:H, ‖a‖≤M ∧ ‖r-Ta‖=β(M)`; same budget; no positivity or range restriction. | Full |
| WR03: nonincreasing | `G.beta_antitone` | Every real ordered pair `0≤M₁≤M₂`; concludes `β(M₂)≤β(M₁)`. This is antitonicity on the printed nonnegative domain. | Full |
| WR03: convex | `G.beta_convex_combination` | Every real `M₁,M₂≥0` and every real `0≤t≤1`; exactly the printed convex-combination inequality, endpoints included. | Full |
| WR03: both sides of Lipschitz inequality | `G.beta_profile_bounds`, also `G.beta_sub_le` | Every `0≤M₁≤M₂`; conjunction `0≤β(M₁)-β(M₂)` and upper bound `‖T‖(M₂-M₁)`. No assumption `M₂>0` survives. | Full |
| WR03 proof endpoint `β(0)=‖r‖` | `G.beta_zero` | Every `T,r`; no nonzero assumption. | Full |
| WR03: `C`, `b`, `q` and floor identity | `P.rangeClosure_coe`, `P.projectedDatum`, `P.residual_sq_decomposition`, `P.projected_residual_eq_infDist`, `P.floor_le_beta` | Closure is norm-topological range closure; `b` is its orthogonal projection; `q` is exactly residual distance. | Full |
| WR03: limit as real `M→∞` | `P.beta_tendsto_floor`, also `P.beta_tendsto_infDist` | `Tendsto (beta T r) atTop (𝓝 ‖r-b‖)` with `beta T r : ℝ→ℝ`. The filter is on real budgets, not on `ℕ` or a selected sequence. | Full |
| WR03: finite-budget floor equality iff budgeted preimage of `b` | `P.beta_eq_floor_iff` | For every `M≥0`, `β(M)=‖r-b‖ ↔ ∃a, Ta=b ∧ ‖a‖≤M`. Both directions; exact range membership. | Full |
| WR03: zero profile iff exact budgeted realization of `r` | `P.beta_eq_zero_iff` | For every `M≥0`, `β(M)=0 ↔ ∃a, Ta=r ∧ ‖a‖≤M`; does not assume the floor is zero or that `r` is already attainable. | Full |
| WR04: every unit-ball dual value bounds profile | `D.dualValue_le_beta` | Every `M≥0` and every `z:Y` with `‖z‖≤1`; correct inner-product order and penalty sign. | Full |
| WR04: maximum is actually attained | `D.exists_attaining_dual_witness` | For every `M≥0`, exists `z:Y`, `‖z‖≤1`, with dual value exactly `β(M)`; no supplied minimizer/variational hypothesis. | Full |
| WR04: literal displayed maximum | `D.sharp_budget_duality` | `IsGreatest` of the image of the closed unit ball under the exact dual objective, at `β(M)`; includes membership and universal upper bound. | Full |
| WR04: strict exclusion | `D.strict_exclusion_certificate` | Any real `ε`, any unit-ball `z`, dual value `>ε` implies `¬∃a, ‖a‖≤M ∧ ‖r-Ta‖≤ε`. The theorem even permits arbitrary `M`; on negative budgets the conclusion is vacuous. | Full |
| WR05: absolute difference of profiles | `R.beta_abs_sub_le` | Same `H,Y`, arbitrary bounded linear `T,S`, arbitrary data `r,s`, all `M≥0`, and both stated norm bounds; conclusion is exactly `|β_{T,r}-β_{S,s}|≤δ+ηM`. | Full |
| WR05: lower certificate from any nominal witness | `R.nominal_dual_lower_certificate` | Every unit-ball `z`, same errors and budget; `⟨s,z⟩-M‖S*z‖-δ-ηM≤β_{T,r}(M)` with no optimization requirement on `z`. | Full |
| Adjacent WR05 candidate residual inequality | `R.candidate_residual_le` | All `a:H`; penalty is `η‖a‖`, not `ηM`; parentheses and additions have the same mathematical value. | Full |
| Additional strict robust exclusion | `R.excludes_budget_of_nominal_dual_certificate` | A strict robust nominal lower value yields a strict lower bound on every feasible actual residual. | Extra valid corollary |

Providing the convex inequality rather than a bundled `ConvexOn` declaration is complete coverage of the printed convexity assertion: it quantifies over every pair in `[0,∞)` and every coefficient in `[0,1]`, which is the defining condition. Likewise the pointwise ordered-pair theorem is complete antitonicity on that domain. No wrappers are required to make either claim universal.

The mathematical statements following WR03 about uniqueness are explanatory prose outside the numbered theorem. The new block proves closedness and convexity of the budget image; its nearest-image-point construction uses the library projection theorem. The four new modules do not add separately named public uniqueness statements for optimal residuals or least-norm preimages. This does not leave any clause of the **WR03 theorem** partial. If future metadata claims that every adjacent prose assertion has a newly named public declaration, that stronger metadata claim would need a separate map.

## Proof dependency and adversarial inspection

### WR03

The formal attainment route differs legitimately from the printed weak-subsequence proof. `isClosed_budget_image` starts with a convergent sequence in the actual image of the closed ball, chooses lifts in that ball, and applies the accepted parent's `exists_solution_of_bounded_approximation` with the **same** real bound `M`. Its conclusion supplies an exact preimage of the sequence limit still in the ball. Metric sequential closedness then proves closedness. Convexity is the direct linear image of the convex ball. The local pinned theorem `exists_norm_eq_iInf_of_complete_convex` then supplies a nearest image point, whose image membership supplies an actual correction. There is no assumed attainment, circular invocation of WR03, or switch from an arbitrary range point to a budgeted lift.

The imported parent's exact type was checked: it concludes `∃a, T a=r ∧ ‖a‖≤M` from bounded approximations, with complete real Hilbert hypotheses and no separability or closed-range parameter. The formal parent's proof uses weak-dual compactness and Riesz; this audit reuses the accepted parent rather than pretending to recompile the whole inherited project.

Convexity uses actual minimizers and feasible convex combinations. Radial shrinking has the denominator `M₂` only inside its positive-budget helper. `beta_sub_le` branches on `M₂=0` versus `M₂>0`; the zero branch forces `M₁=0`. The public combined bound retains no denominator hypothesis.

The real-budget limit picks a single range approximation at the chosen tolerance, then uses the event `M≥‖a‖` in real `atTop`. Its lower comparison derives `M≥0` from that event. Thus the proof covers every sufficiently large real budget and does not silently establish only integer or sequential convergence. It proves the limit even without source completeness; omission of `[CompleteSpace H]` in this theorem is a valid strengthening.

The two iff proofs choose attained minimizers only under `M≥0`; the floor proof uses the exact norm-square decomposition, while the zero proof directly turns a zero residual norm into `Ta=r`. No implication from an unrestricted zero infimum to exact realizability occurs.

### WR04

`dualValue_le_residual` checks every candidate and every unit-ball witness via the adjoint identity and Cauchy–Schwarz. `minimizer_variational` translates an attained correction into an image-point minimizer and applies the pinned `norm_eq_iInf_iff_real_inner_le_zero`; the source of that library theorem was read and confirms the exact one-sided variational condition for a convex set. It does not require positive radius, nonzero residual, closed range, or finite dimension.

`ball_support_eq` splits `g=0` before normalizing. In the nonzero branch its test vector is `(M/‖g‖) • g`, whose norm is `M`, including `M=0`. There is no division by `M`. `exists_sharp_witness_of_variational` splits the residual zero case first, using `z=0`; the nonzero branch normalizes the residual, gets exact ball support, and subtracts the support penalty. The final public witness theorem supplies all helper assumptions internally from WR03 attainment.

`IsGreatest S β` asserts both `β∈S` and `β` is an upper bound for `S`. Here `S` is exactly the image of `Metric.closedBall (0:Y) 1` under `z↦⟨r,z⟩−M‖T*z‖`. Consequently this is the literal maximum in WR04; it is stronger than a statement only about `sSup S` or a nonattained supremum.

### WR05

The candidate error identity has the correct sign: `(r-Ta)-(s-Sa)=(r-s)-(T-S)a`. The absolute residual-norm bound then follows from the reverse triangle inequality. The profile comparison evaluates the first profile at an attained minimizer of the second using the same ball. Reversing both operator and data differences preserves their norms and supplies the other half. `abs_le` packages both directions without losing the lower bound.

The nominal certificate uses the lower half of this absolute comparison and nominal weak duality. Its penalty is exactly `δ+ηM`, subtracted from the nominal dual value. It has no hidden assumption that the nominal witness maximizes, that the minimizers agree, or that a protection kernel may change.

### Boundary obligations

| Boundary or hostile reinterpretation | Audit result |
|---|---|
| `M=0` | Passed: explicit profile theorem, zero branch in Lipschitz proof, and support test vector of norm zero. Final theorem types admit zero. |
| Zero optimal residual | Passed: dual witness constructed as zero; no residual normalization in that branch. |
| `T*z=0` | Passed: zero support vector branch; no division by its norm. |
| `T=0` / `‖T‖=0` | Passed: no nonzero operator hypothesis; all formulas specialize to the constant profile `‖r‖`. |
| Zero-dimensional source or target | Passed: no `Nontrivial` hypothesis; unit ball includes zero. |
| Noninjective operator | Passed: no inverse or unique correction used; only existence and image geometry. |
| Dense nonclosed range | Passed: projection is onto closure; finite-ball closedness comes from same-budget WR01, not closed range. |
| Nonseparable spaces | Passed: no countable-basis or separability class in exported types or new proof route. |
| Convexity endpoints / equal budgets | Passed: weak inequalities on `t` and budgets; no strict-order hypothesis in final shape theorems. |
| Negative error constants | No extra assumption needed: the two norm bounds already force both constants nonnegative. |
| Different correction spaces / changed preservation kernels | Correctly excluded: `T` and `S` must share the same `H` and its norm. The types cannot express an unaccounted moving-kernel comparison. |
| Unit sphere substituted for unit ball | Correctly excluded: all witness results use `≤1`, including the essential zero witness. |
| Regularized budgets substituted for every budget | Correctly excluded: no parameter `α` or regularization assumption appears in the final types. |
| Source completeness omitted by a helper | Safe: the final target still holds under complete `H`; some helper/limit results are stronger. |

## Remaining obligations and trust boundary

**Exact remaining statement/proof gap for WR03–WR05: none at the four frozen hashes.** The full target claims are covered. The new code depends on the accepted parent same-budget realization theorem and pinned mathlib's standard Hilbert/metric/convex constructions. The only logical axioms reported by the new declaration closures are the accepted standard three listed above.

This fresh audit rebuild intentionally reuses accepted inherited `.olean` files and pinned external caches. It is therefore a fresh build of the four new source modules, not a clean source build of the whole inherited project. Parent cache/source provenance, aggregate theorem inventory, negative controls, publication status edits, and final package receipts remain the root integration workflow's responsibility. The audit does not promote status merely from an author's source map or old per-module receipt. At delivery, all four source hashes were checked again and remained unchanged.

## Appendix: exact independent type and axiom export

The following is the successful exporter stdout, including all definitions, the range-closure completeness instance, and every theorem. It preserves complete binder lists and exposes hypotheses that a shortened source excerpt could hide.

```text
@KomorebiSpace.BudgetProfile.beta : {H : Type u_1} →
  {Y : Type u_2} →
    [inst : NormedAddCommGroup H] →
      [inst_1 : InnerProductSpace ℝ H] →
        [inst_2 : NormedAddCommGroup Y] → [inst_3 : InnerProductSpace ℝ Y] → (H →L[ℝ] Y) → Y → ℝ → ℝ
'KomorebiSpace.BudgetProfile.beta' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.convex_budget_image : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y] [inst_3 : InnerProductSpace ℝ Y] (T : H →L[ℝ] Y)
  (M : ℝ), Convex ℝ (⇑T '' Metric.closedBall 0 M)
'KomorebiSpace.BudgetProfile.convex_budget_image' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.isClosed_budget_image : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [CompleteSpace H] [inst_3 : NormedAddCommGroup Y] [inst_4 : InnerProductSpace ℝ Y]
  [CompleteSpace Y] (T : H →L[ℝ] Y) (M : ℝ), IsClosed (⇑T '' Metric.closedBall 0 M)
'KomorebiSpace.BudgetProfile.isClosed_budget_image' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.budget_image_nonempty : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y] [inst_3 : InnerProductSpace ℝ Y] (T : H →L[ℝ] Y)
  {M : ℝ}, 0 ≤ M → (⇑T '' Metric.closedBall 0 M).Nonempty
'KomorebiSpace.BudgetProfile.budget_image_nonempty' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.beta_nonneg : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y] [inst_3 : InnerProductSpace ℝ Y] (T : H →L[ℝ] Y)
  (r : Y) (M : ℝ), 0 ≤ KomorebiSpace.BudgetProfile.beta T r M
'KomorebiSpace.BudgetProfile.beta_nonneg' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.beta_le_residual : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y] [inst_3 : InnerProductSpace ℝ Y] (T : H →L[ℝ] Y)
  (r : Y) {M : ℝ} {a : H}, ‖a‖ ≤ M → KomorebiSpace.BudgetProfile.beta T r M ≤ ‖r - T a‖
'KomorebiSpace.BudgetProfile.beta_le_residual' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.exists_budget_minimizer : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [CompleteSpace H] [inst_3 : NormedAddCommGroup Y] [inst_4 : InnerProductSpace ℝ Y]
  [CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y) {M : ℝ},
  0 ≤ M → ∃ (a : H), ‖a‖ ≤ M ∧ ‖r - T a‖ = KomorebiSpace.BudgetProfile.beta T r M
'KomorebiSpace.BudgetProfile.exists_budget_minimizer' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.beta_eq_iInf : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [CompleteSpace H] [inst_3 : NormedAddCommGroup Y] [inst_4 : InnerProductSpace ℝ Y]
  [CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y) {M : ℝ},
  0 ≤ M → KomorebiSpace.BudgetProfile.beta T r M = ⨅ (a : { a : H // ‖a‖ ≤ M }), ‖r - T ↑a‖
'KomorebiSpace.BudgetProfile.beta_eq_iInf' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.rangeClosure : {H : Type u_1} →
  {Y : Type u_2} →
    [inst : NormedAddCommGroup H] →
      [inst_1 : InnerProductSpace ℝ H] →
        [inst_2 : NormedAddCommGroup Y] → [inst_3 : InnerProductSpace ℝ Y] → (H →L[ℝ] Y) → Submodule ℝ Y
'KomorebiSpace.BudgetProfile.rangeClosure' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.rangeClosure_coe : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y] [inst_3 : InnerProductSpace ℝ Y] (T : H →L[ℝ] Y),
  ↑(KomorebiSpace.BudgetProfile.rangeClosure T) = closure (Set.range ⇑T)
'KomorebiSpace.BudgetProfile.rangeClosure_coe' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.rangeClosure_completeSpace : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y] [inst_3 : InnerProductSpace ℝ Y] [CompleteSpace Y]
  (T : H →L[ℝ] Y), CompleteSpace ↥(KomorebiSpace.BudgetProfile.rangeClosure T)
'KomorebiSpace.BudgetProfile.rangeClosure_completeSpace' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.projectedDatum : {H : Type u_1} →
  {Y : Type u_2} →
    [inst : NormedAddCommGroup H] →
      [inst_1 : InnerProductSpace ℝ H] →
        [inst_2 : NormedAddCommGroup Y] → [inst_3 : InnerProductSpace ℝ Y] → [CompleteSpace Y] → (H →L[ℝ] Y) → Y → Y
'KomorebiSpace.BudgetProfile.projectedDatum' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.projectedDatum_mem : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y] [inst_3 : InnerProductSpace ℝ Y]
  [inst_4 : CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y),
  KomorebiSpace.BudgetProfile.projectedDatum T r ∈ KomorebiSpace.BudgetProfile.rangeClosure T
'KomorebiSpace.BudgetProfile.projectedDatum_mem' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.apply_mem_rangeClosure : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y] [inst_3 : InnerProductSpace ℝ Y] (T : H →L[ℝ] Y)
  (a : H), T a ∈ KomorebiSpace.BudgetProfile.rangeClosure T
'KomorebiSpace.BudgetProfile.apply_mem_rangeClosure' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.residual_sq_decomposition : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y] [inst_3 : InnerProductSpace ℝ Y]
  [inst_4 : CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y) (a : H),
  ‖r - T a‖ ^ 2 =
    ‖r - KomorebiSpace.BudgetProfile.projectedDatum T r‖ ^ 2 +
      ‖KomorebiSpace.BudgetProfile.projectedDatum T r - T a‖ ^ 2
'KomorebiSpace.BudgetProfile.residual_sq_decomposition' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.projected_residual_eq_infDist : ∀ {H : Type u_1} {Y : Type u_2}
  [inst : NormedAddCommGroup H] [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y]
  [inst_3 : InnerProductSpace ℝ Y] [inst_4 : CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y),
  ‖r - KomorebiSpace.BudgetProfile.projectedDatum T r‖ = Metric.infDist r (closure (Set.range ⇑T))
'KomorebiSpace.BudgetProfile.projected_residual_eq_infDist' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.floor_le_beta : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y] [inst_3 : InnerProductSpace ℝ Y]
  [inst_4 : CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y) {M : ℝ},
  0 ≤ M → ‖r - KomorebiSpace.BudgetProfile.projectedDatum T r‖ ≤ KomorebiSpace.BudgetProfile.beta T r M
'KomorebiSpace.BudgetProfile.floor_le_beta' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.beta_eq_floor_iff : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [CompleteSpace H] [inst_3 : NormedAddCommGroup Y] [inst_4 : InnerProductSpace ℝ Y]
  [inst_5 : CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y) {M : ℝ},
  0 ≤ M →
    (KomorebiSpace.BudgetProfile.beta T r M = ‖r - KomorebiSpace.BudgetProfile.projectedDatum T r‖ ↔
      ∃ (a : H), T a = KomorebiSpace.BudgetProfile.projectedDatum T r ∧ ‖a‖ ≤ M)
'KomorebiSpace.BudgetProfile.beta_eq_floor_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.beta_eq_zero_iff : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [CompleteSpace H] [inst_3 : NormedAddCommGroup Y] [inst_4 : InnerProductSpace ℝ Y]
  [CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y) {M : ℝ},
  0 ≤ M → (KomorebiSpace.BudgetProfile.beta T r M = 0 ↔ ∃ (a : H), T a = r ∧ ‖a‖ ≤ M)
'KomorebiSpace.BudgetProfile.beta_eq_zero_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.beta_tendsto_infDist : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y] [inst_3 : InnerProductSpace ℝ Y] [CompleteSpace Y]
  (T : H →L[ℝ] Y) (r : Y),
  Filter.Tendsto (KomorebiSpace.BudgetProfile.beta T r) Filter.atTop (nhds (Metric.infDist r (closure (Set.range ⇑T))))
'KomorebiSpace.BudgetProfile.beta_tendsto_infDist' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfile.beta_tendsto_floor : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y] [inst_3 : InnerProductSpace ℝ Y]
  [inst_4 : CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y),
  Filter.Tendsto (KomorebiSpace.BudgetProfile.beta T r) Filter.atTop
    (nhds ‖r - KomorebiSpace.BudgetProfile.projectedDatum T r‖)
'KomorebiSpace.BudgetProfile.beta_tendsto_floor' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfileGeometry.beta_antitone : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [CompleteSpace H] [inst_3 : NormedAddCommGroup Y] [inst_4 : InnerProductSpace ℝ Y]
  [CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y) {M₁ M₂ : ℝ},
  0 ≤ M₁ → M₁ ≤ M₂ → KomorebiSpace.BudgetProfile.beta T r M₂ ≤ KomorebiSpace.BudgetProfile.beta T r M₁
'KomorebiSpace.BudgetProfileGeometry.beta_antitone' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfileGeometry.beta_zero : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [CompleteSpace H] [inst_3 : NormedAddCommGroup Y] [inst_4 : InnerProductSpace ℝ Y]
  [CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y), KomorebiSpace.BudgetProfile.beta T r 0 = ‖r‖
'KomorebiSpace.BudgetProfileGeometry.beta_zero' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfileGeometry.beta_convex_combination : ∀ {H : Type u_1} {Y : Type u_2}
  [inst : NormedAddCommGroup H] [inst_1 : InnerProductSpace ℝ H] [CompleteSpace H] [inst_3 : NormedAddCommGroup Y]
  [inst_4 : InnerProductSpace ℝ Y] [CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y) {M₁ M₂ t : ℝ},
  0 ≤ M₁ →
    0 ≤ M₂ →
      0 ≤ t →
        t ≤ 1 →
          KomorebiSpace.BudgetProfile.beta T r (t * M₁ + (1 - t) * M₂) ≤
            t * KomorebiSpace.BudgetProfile.beta T r M₁ + (1 - t) * KomorebiSpace.BudgetProfile.beta T r M₂
'KomorebiSpace.BudgetProfileGeometry.beta_convex_combination' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfileGeometry.radial_shrink_bounds : ∀ {H : Type u_1} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] {a : H} {M₁ M₂ : ℝ},
  0 ≤ M₁ → 0 < M₂ → M₁ ≤ M₂ → ‖a‖ ≤ M₂ → ‖(M₁ / M₂) • a‖ ≤ M₁ ∧ ‖a - (M₁ / M₂) • a‖ ≤ M₂ - M₁
'KomorebiSpace.BudgetProfileGeometry.radial_shrink_bounds' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfileGeometry.beta_sub_le : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [CompleteSpace H] [inst_3 : NormedAddCommGroup Y] [inst_4 : InnerProductSpace ℝ Y]
  [CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y) {M₁ M₂ : ℝ},
  0 ≤ M₁ → M₁ ≤ M₂ → KomorebiSpace.BudgetProfile.beta T r M₁ - KomorebiSpace.BudgetProfile.beta T r M₂ ≤ ‖T‖ * (M₂ - M₁)
'KomorebiSpace.BudgetProfileGeometry.beta_sub_le' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetProfileGeometry.beta_profile_bounds : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [CompleteSpace H] [inst_3 : NormedAddCommGroup Y] [inst_4 : InnerProductSpace ℝ Y]
  [CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y) {M₁ M₂ : ℝ},
  0 ≤ M₁ →
    M₁ ≤ M₂ →
      0 ≤ KomorebiSpace.BudgetProfile.beta T r M₁ - KomorebiSpace.BudgetProfile.beta T r M₂ ∧
        KomorebiSpace.BudgetProfile.beta T r M₁ - KomorebiSpace.BudgetProfile.beta T r M₂ ≤ ‖T‖ * (M₂ - M₁)
'KomorebiSpace.BudgetProfileGeometry.beta_profile_bounds' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetDuality.dualValue_le_residual : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : CompleteSpace H] [inst_3 : NormedAddCommGroup Y]
  [inst_4 : InnerProductSpace ℝ Y] [inst_5 : CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y) {M : ℝ} {a : H},
  ‖a‖ ≤ M → ∀ {z : Y}, ‖z‖ ≤ 1 → inner ℝ r z - M * ‖(ContinuousLinearMap.adjoint T) z‖ ≤ ‖r - T a‖
'KomorebiSpace.BudgetDuality.dualValue_le_residual' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetDuality.ball_support_eq : ∀ {H : Type u_1} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] {M : ℝ},
  0 ≤ M → ∀ (g a : H), ‖a‖ ≤ M → (∀ (b : H), ‖b‖ ≤ M → inner ℝ b g ≤ inner ℝ a g) → inner ℝ a g = M * ‖g‖
'KomorebiSpace.BudgetDuality.ball_support_eq' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetDuality.exists_sharp_witness_of_variational : ∀ {H : Type u_1} {Y : Type u_2}
  [inst : NormedAddCommGroup H] [inst_1 : InnerProductSpace ℝ H] [inst_2 : CompleteSpace H]
  [inst_3 : NormedAddCommGroup Y] [inst_4 : InnerProductSpace ℝ Y] [inst_5 : CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y)
  {M : ℝ},
  0 ≤ M →
    ∀ (a : H),
      ‖a‖ ≤ M →
        (∀ (b : H), ‖b‖ ≤ M → inner ℝ (r - T a) (T b - T a) ≤ 0) →
          ∃ (z : Y), ‖z‖ ≤ 1 ∧ inner ℝ r z - M * ‖(ContinuousLinearMap.adjoint T) z‖ = ‖r - T a‖
'KomorebiSpace.BudgetDuality.exists_sharp_witness_of_variational' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
@KomorebiSpace.BudgetDuality.dualValue_le_beta : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : CompleteSpace H] [inst_3 : NormedAddCommGroup Y]
  [inst_4 : InnerProductSpace ℝ Y] [inst_5 : CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y) {M : ℝ},
  0 ≤ M →
    ∀ {z : Y}, ‖z‖ ≤ 1 → inner ℝ r z - M * ‖(ContinuousLinearMap.adjoint T) z‖ ≤ KomorebiSpace.BudgetProfile.beta T r M
'KomorebiSpace.BudgetDuality.dualValue_le_beta' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetDuality.minimizer_variational : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y] [inst_3 : InnerProductSpace ℝ Y] (T : H →L[ℝ] Y)
  (r : Y) {M : ℝ} (a : H),
  ‖a‖ ≤ M → ‖r - T a‖ = KomorebiSpace.BudgetProfile.beta T r M → ∀ (b : H), ‖b‖ ≤ M → inner ℝ (r - T a) (T b - T a) ≤ 0
'KomorebiSpace.BudgetDuality.minimizer_variational' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetDuality.exists_attaining_dual_witness : ∀ {H : Type u_1} {Y : Type u_2}
  [inst : NormedAddCommGroup H] [inst_1 : InnerProductSpace ℝ H] [inst_2 : CompleteSpace H]
  [inst_3 : NormedAddCommGroup Y] [inst_4 : InnerProductSpace ℝ Y] [inst_5 : CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y)
  {M : ℝ},
  0 ≤ M →
    ∃ (z : Y), ‖z‖ ≤ 1 ∧ inner ℝ r z - M * ‖(ContinuousLinearMap.adjoint T) z‖ = KomorebiSpace.BudgetProfile.beta T r M
'KomorebiSpace.BudgetDuality.exists_attaining_dual_witness' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetDuality.sharp_budget_duality : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : CompleteSpace H] [inst_3 : NormedAddCommGroup Y]
  [inst_4 : InnerProductSpace ℝ Y] [inst_5 : CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y) {M : ℝ},
  0 ≤ M →
    IsGreatest ((fun (z : Y) => inner ℝ r z - M * ‖(ContinuousLinearMap.adjoint T) z‖) '' Metric.closedBall 0 1)
      (KomorebiSpace.BudgetProfile.beta T r M)
'KomorebiSpace.BudgetDuality.sharp_budget_duality' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetDuality.strict_exclusion_certificate : ∀ {H : Type u_1} {Y : Type u_2}
  [inst : NormedAddCommGroup H] [inst_1 : InnerProductSpace ℝ H] [inst_2 : CompleteSpace H]
  [inst_3 : NormedAddCommGroup Y] [inst_4 : InnerProductSpace ℝ Y] [inst_5 : CompleteSpace Y] (T : H →L[ℝ] Y) (r : Y)
  {M ε : ℝ} {z : Y},
  ‖z‖ ≤ 1 → ε < inner ℝ r z - M * ‖(ContinuousLinearMap.adjoint T) z‖ → ¬∃ (a : H), ‖a‖ ≤ M ∧ ‖r - T a‖ ≤ ε
'KomorebiSpace.BudgetDuality.strict_exclusion_certificate' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetRobustness.candidate_residual_difference_bound : ∀ {H : Type u_1} {Y : Type u_2}
  [inst : NormedAddCommGroup H] [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y]
  [inst_3 : InnerProductSpace ℝ Y] (T S : H →L[ℝ] Y) (r s : Y) {η δ : ℝ},
  ‖T - S‖ ≤ η → ‖r - s‖ ≤ δ → ∀ (a : H), ‖r - T a - (s - S a)‖ ≤ δ + η * ‖a‖
'KomorebiSpace.BudgetRobustness.candidate_residual_difference_bound' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
@KomorebiSpace.BudgetRobustness.candidate_residual_abs_bound : ∀ {H : Type u_1} {Y : Type u_2}
  [inst : NormedAddCommGroup H] [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y]
  [inst_3 : InnerProductSpace ℝ Y] (T S : H →L[ℝ] Y) (r s : Y) {η δ : ℝ},
  ‖T - S‖ ≤ η → ‖r - s‖ ≤ δ → ∀ (a : H), |‖r - T a‖ - ‖s - S a‖| ≤ δ + η * ‖a‖
'KomorebiSpace.BudgetRobustness.candidate_residual_abs_bound' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetRobustness.candidate_residual_le : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y] [inst_3 : InnerProductSpace ℝ Y] (T S : H →L[ℝ] Y)
  (r s : Y) {η δ : ℝ}, ‖T - S‖ ≤ η → ‖r - s‖ ≤ δ → ∀ (a : H), ‖r - T a‖ ≤ ‖s - S a‖ + δ + η * ‖a‖
'KomorebiSpace.BudgetRobustness.candidate_residual_le' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetRobustness.budget_candidate_residual_abs_bound : ∀ {H : Type u_1} {Y : Type u_2}
  [inst : NormedAddCommGroup H] [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y]
  [inst_3 : InnerProductSpace ℝ Y] (T S : H →L[ℝ] Y) (r s : Y) {η δ M : ℝ},
  0 ≤ η → ‖T - S‖ ≤ η → ‖r - s‖ ≤ δ → ∀ {a : H}, ‖a‖ ≤ M → |‖r - T a‖ - ‖s - S a‖| ≤ δ + η * M
'KomorebiSpace.BudgetRobustness.budget_candidate_residual_abs_bound' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
@KomorebiSpace.BudgetRobustness.beta_le_beta_add_uncertainty : ∀ {H : Type u_1} {Y : Type u_2}
  [inst : NormedAddCommGroup H] [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y]
  [inst_3 : InnerProductSpace ℝ Y] [CompleteSpace H] [CompleteSpace Y] (T S : H →L[ℝ] Y) (r s : Y) {η δ M : ℝ},
  0 ≤ M →
    ‖T - S‖ ≤ η →
      ‖r - s‖ ≤ δ → KomorebiSpace.BudgetProfile.beta T r M ≤ KomorebiSpace.BudgetProfile.beta S s M + (δ + η * M)
'KomorebiSpace.BudgetRobustness.beta_le_beta_add_uncertainty' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetRobustness.beta_abs_sub_le : ∀ {H : Type u_1} {Y : Type u_2} [inst : NormedAddCommGroup H]
  [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y] [inst_3 : InnerProductSpace ℝ Y] [CompleteSpace H]
  [CompleteSpace Y] (T S : H →L[ℝ] Y) (r s : Y) {η δ M : ℝ},
  0 ≤ M →
    ‖T - S‖ ≤ η →
      ‖r - s‖ ≤ δ → |KomorebiSpace.BudgetProfile.beta T r M - KomorebiSpace.BudgetProfile.beta S s M| ≤ δ + η * M
'KomorebiSpace.BudgetRobustness.beta_abs_sub_le' depends on axioms: [propext, Classical.choice, Quot.sound]
@KomorebiSpace.BudgetRobustness.nominal_dual_lower_certificate : ∀ {H : Type u_1} {Y : Type u_2}
  [inst : NormedAddCommGroup H] [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y]
  [inst_3 : InnerProductSpace ℝ Y] [inst_4 : CompleteSpace H] [inst_5 : CompleteSpace Y] (T S : H →L[ℝ] Y) (r s : Y)
  {η δ M : ℝ},
  0 ≤ M →
    ‖T - S‖ ≤ η →
      ‖r - s‖ ≤ δ →
        ∀ {z : Y},
          ‖z‖ ≤ 1 →
            inner ℝ s z - M * ‖(ContinuousLinearMap.adjoint S) z‖ - δ - η * M ≤ KomorebiSpace.BudgetProfile.beta T r M
'KomorebiSpace.BudgetRobustness.nominal_dual_lower_certificate' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
@KomorebiSpace.BudgetRobustness.excludes_budget_of_nominal_dual_certificate : ∀ {H : Type u_1} {Y : Type u_2}
  [inst : NormedAddCommGroup H] [inst_1 : InnerProductSpace ℝ H] [inst_2 : NormedAddCommGroup Y]
  [inst_3 : InnerProductSpace ℝ Y] [inst_4 : CompleteSpace H] [inst_5 : CompleteSpace Y] (T S : H →L[ℝ] Y) (r s : Y)
  {η δ M ε : ℝ},
  0 ≤ M →
    ‖T - S‖ ≤ η →
      ‖r - s‖ ≤ δ →
        ∀ {z : Y},
          ‖z‖ ≤ 1 →
            ε < inner ℝ s z - M * ‖(ContinuousLinearMap.adjoint S) z‖ - δ - η * M → ∀ {a : H}, ‖a‖ ≤ M → ε < ‖r - T a‖
'KomorebiSpace.BudgetRobustness.excludes_budget_of_nominal_dual_certificate' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
```
