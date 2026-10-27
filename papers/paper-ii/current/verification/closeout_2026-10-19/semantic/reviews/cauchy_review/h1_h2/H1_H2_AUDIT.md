# H1 holomorphy and H2 decay: independent source audit

**Normalized claim.** Let `Γ : IntegralCycle` be the actual finite family represented by its integrable velocities. Let `E` be a complex Banach space, with compatible real scalar structure. For every open `U ⊆ ℂ`, every `f : ℂ → E` complex differentiable on `U`, and `Γ.trace ⊆ U`, the function `w ↦ Γ.lineIntegral (dslope f w)` is complex differentiable on `U`. For every density continuous on `Γ.trace`, the actual Cauchy transform `w ↦ Γ.lineIntegral (fun z => (z-w)⁻¹ • f z)` tends to zero along `cocompact ℂ`.

**Primary verdict: proved as written.** This is an independent raw-source mathematical audit; it is not a fresh compilation or an independent axiom-closure check. No source was edited and no Lean process was launched for this review.

## Claim card and exact revisions

H1 is `Komorebi.PaperII.ReleaseCycleDSlope.differentiableOn_lineIntegral_dslope`, lines 287–315 of `cauchy/dslope/ReleaseCycleDSlope.lean`, SHA256 `4377235c25789855dfebd94f24f6574cf58697a35f5581e96ec6aa166056f39c`.

H2 is `Komorebi.PaperII.ReleaseCycleDecay.dixonH2_tendsto_zero`, lines 72–79 of `cauchy/dslope/ReleaseCycleDecay.lean`, SHA256 `7d2ee803020f2c05b1b5642a8a4494a33a26d8ef71000671fbaf5cd5bc59fad4`.

`IntegralCycle` is a natural-number-indexed finite family with `base : Fin count → ℂ`, `velocity : Fin count → ℝ → ℂ`, an `IntervalIntegrable` witness on `0..1` for each velocity, and zero integral of each velocity. Its curve is `base + ∫₀ˢ velocity`; its trace is the union of the images of `uIcc 0 1`; its line integral is the sum of `∫₀¹ velocity • density(curve)`; its length is the sum of the integrals of velocity norms. These definitions are in `ReleaseAnalyticContour.lean`, lines 19–37 and 55–57. The exact dependency hash is in the JSON.

H1 explicitly quantifies a general `E : Type*` with `NormedAddCommGroup`, complex and real `NormedSpace`, `IsScalarTower ℝ ℂ E`, and `CompleteSpace E`. There is no finite-dimensional hypothesis. H2 is stronger than required in target-space scope: it does not require completeness or a scalar-tower hypothesis. It requires only continuity of the density on the compact trace, and has no domain `U` hypothesis. Neither theorem assumes a velocity bound, piecewise smoothness, a simple loop, a nonempty family, or a nonzero velocity.

## Dependency graph

1. Defining integrable velocities → continuous primitive curves → compact finite trace (`ReleaseCycleParameter.isCompact_trace`). This is an internal proof using standard interval-integral continuity and compact finite unions.
2. Holomorphic `f` on an open convex neighborhood → continuous `deriv f` → the segment integral formula for `dslope` (`dslope_eq_integral_deriv`). The external leaves are pinned Mathlib's analytic regularity and unit-interval fundamental theorem of calculus.
3. That formula plus a compact tube → joint continuity on convex open sets. Local convex balls on the diagonal and the explicit quotient off the diagonal → joint continuity on arbitrary open `U` (`continuousOn_dslope_prod_open`).
4. Joint continuity on `K_c × closedBall w₀ (3ρ/2)` → one uniform norm bound there. Mathlib's Banach-valued removable-singularity theorem makes each `dslope f c` holomorphic throughout `U`, including `c`. Its Cauchy derivative estimate on radius `ρ/2` circles → `deriv_dslope_bounded_on_compact_open`.
5. `dslope_comm` plus `deriv_dslope_eq_repeated` → the actual first-node derivative `dslope (dslope f a) a z`. A second application of the removable-singularity theorem gives continuity of this derivative as a function of `z` at the center parameter.
6. The uniform derivative bound and actual velocity integrability → differentiation under each actual interval integral → finite sum differentiation (`hasDerivAt_lineIntegral`) → H1.
7. Compact trace and continuous density → finite radius and norm bounds. Reverse triangle inequality + `norm_lineIntegral_le` → reciprocal estimate → an explicit epsilon argument outside a closed ball → H2.

No target theorem depends back on itself, on the general finite-cycle Cauchy theorem, or on an original-rectifiable-contour identification. The local Cauchy/removable-singularity facts used here are existing Mathlib theorems about complex differentiable Banach-valued functions.

## Obligation matrix

| Obligation | Status | Decisive source evidence |
|---|---|---|
| Actual integral-cycle object, rather than a scalar or smooth surrogate | passed | `IntegralCycle.lineIntegral` is unfolded in `hasDerivAt_lineIntegral`; each summand uses the supplied velocity. |
| Arbitrary open, possibly disconnected or nonconvex `U` | passed | `continuousOn_dslope_prod_open`, lines 165–193: only a local convex ball is used on the diagonal; the off-diagonal argument uses the quotient. The final H1 statement has only `IsOpen U`. |
| Diagonal divided-difference value and first-node holomorphy | passed | `dslope` is derivative-valued on the diagonal. Mathlib `Complex.differentiableOn_dslope` applies on the neighborhood `U`; symmetry converts its second-node holomorphy into the derivative needed in H1, lines 296–305. |
| Compact uniformity over every trace point | passed | `deriv_dslope_bounded_on_compact_open`, lines 210–246, chooses one radius near `w₀` and one bound over `K_c × closedBall`. The specialization is `K_c = Γ.trace`, lines 292–293. |
| Correct derivative and derivative continuity in the integration variable | passed | `deriv_dslope_eq_repeated`, lines 258–280, follows from differentiating `(z-c) • dslope g c z = g z - g c`. H1 lines 307–309 use holomorphy of the repeated divided difference to supply continuity on the trace. |
| Integrable domination independent of the integration variable's neighborhood | passed | `ReleaseCycleParameter.hasDerivAt_lineIntegral`, lines 42–76, uses one parameter neighborhood `s`, bound `‖velocity i t‖ * M`, and `velocity_integrable.norm.mul_const M`. |
| No finite-dimensional restriction on `E` | passed | Generic Banach hypotheses in H1 and the exact generic `E` signatures of Mathlib's removable-singularity theorem and Cauchy estimate. |
| H2 tends to zero for continuous trace densities | passed | `dixonH2_tendsto_zero`, lines 72–79, supplies bounds from compactness; the denominator is positive outside `R < ‖w‖`; lines 19–35 supply the epsilon proof. |
| Empty family, constant loops, repeats, unbounded integrable velocities | passed | The trace proof is a finite union, the integral is a `Fin count` sum, and all velocity estimates are integral estimates. No nonemptiness, injectivity, nonzero speed, or pointwise velocity bound enters. |
| A standalone two-variable holomorphy declaration for `(c,w) ↦ dslope f c w` | not addressed | This module proves joint continuity and the exact one-variable holomorphy/derivative needed by H1. It does not state or invoke a theorem asserting complex differentiability from `ℂ × ℂ` into `E`. This is not a gap in the stated H1 claim. |
| Identification with every original rectifiable parametrization or canonical calculus | out of scope | These are separate representation and identification bridges, not hypotheses or conclusions of H1/H2. |
| Fresh compile and transitive axiom inventory | not addressed | No compile was authorized for this reviewer; the parent owns compilation. |

## Decisive derivations

For the derivative bound, choose `ρ = ρ_w/4`, where `ball w₀ ρ_w ⊆ U`. The compact product `Γ.trace × closedBall w₀ (3ρ/2)` lies in `U × U`; joint continuity bounds `dslope f c z` there by a common `max M 0`. For `w ∈ ball w₀ (ρ/2)`, the radius `ρ/2` closed ball about `w` lies inside that same larger ball. The exact Mathlib Cauchy estimate therefore bounds `‖deriv (dslope f c) w‖` by `max M 0 / (ρ/2)`. The source uses a larger positive constant by adding `1`.

For each curve, the parameter integral has integrand `F(a,t)=velocity_i(t) • dslope f a (curve_i(t))`. Its parameter derivative is `velocity_i(t) • dslope (dslope f a) a (curve_i(t))`, whose norm is bounded by `‖velocity_i(t)‖ * M` on one common neighborhood of the parameter. That bound is interval integrable. The source supplies eventual strong measurability, center integrability, derivative strong measurability at the center, the bound, bound integrability, and the pointwise derivative required by `intervalIntegral.hasDerivAt_integral_of_dominated_loc_of_deriv_le`. No differentiation of the curve or its velocity is used.

For H2, if `‖z‖ ≤ R < ‖w‖`, then `0 < ‖w‖-R ≤ ‖z-w‖`, hence `‖(z-w)⁻¹ • f z‖ ≤ M/(‖w‖-R)`. The actual integral estimate yields `‖H2(w)‖ ≤ Γ.length*M/(‖w‖-R)`. The eventual condition `max R (R+C/ε) < ‖w‖`, with `C=Γ.length*M`, directly gives `‖H2(w)‖ < ε`. Compactness supplies `R` and `M=max M₀ 0` even for an empty trace. For continuous densities, the far-field kernel density is continuous on the trace, so these are genuine integrable line integrands. The more general raw bound theorem accepts merely bounded densities using Lean's totalized Bochner-integral convention; H2's continuous-density conclusion does not rely on a nonintegrable interpretation.

## Source checks, remaining gap, and next check

The review read both entire candidate files, the complete parameter-integral dependency, the defining/integral part of `ReleaseAnalyticContour.lean`, and the exact local Mathlib definitions and theorem signatures for `dslope`, removable singularities, the Cauchy estimate, dominated continuity/differentiation and the fundamental theorem of calculus. SHA256 values were recomputed. Searches found no `sorry`, `admit`, new `axiom`, `unsafe`, `opaque`, or `FiniteDimensional` token in the two candidates or `ReleaseCycleParameter.lean`. There was no applicable `AGENTS.md` or local `.mathbox` ledger observed. Author verification JSON and provenance claims were not used as proof evidence.

No mathematical implication remains missing for the normalized H1/H2 claims. The strongest safe statement is exactly those claims for actual `IntegralCycle` line integrals, with no extra regularity or finite-dimensional restrictions. The cheapest remaining formal check is the parent's fresh strict elaboration and transitive axiom audit against these exact hashes and the pinned dependency closure. A separate claim of joint two-variable holomorphy would require its own declaration/proof or exact source; it should not be described as the formal conclusion of this module.

Review provenance: independent focused raw-source review by `/root/paper_ii_length_review/h1_h2_review`, with a separately delegated raw-source check of the parameter domination theorem. No author proof verdict was relied on. Audit date: 2026-10-19. Mathlib manifest revision: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`; all directly inspected theorem files are hashed in the JSON.
