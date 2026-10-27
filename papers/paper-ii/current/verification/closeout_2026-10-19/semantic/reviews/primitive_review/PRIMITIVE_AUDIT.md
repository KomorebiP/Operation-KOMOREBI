# Independent scalar primitive cancellation audit

**Verdict: proved as written**, for `ReleaseCyclePrimitive.lean` SHA256 `194eedd37733f6403438766e0f054e6cb5f9e57f92d326053b4c13d115cf39c8`. This covers the seven declarations culminating in `IntegralCycle.lineIntegral_deriv_eq_zero`. I made no source edits.

The normalized claim is: given an actual finite `IntegralCycle Γ`, an open `U ⊆ ℂ` containing its complete trace, and a supplied `F : ℂ → ℂ` holomorphic on `U`,

\[
\int_0^1 v_i(s) F'(\gamma_i(s))\,ds=F(\gamma_i(1))-F(\gamma_i(0)),
\qquad \Gamma.\operatorname{lineIntegral}(F')=0.
\]

Here `γᵢ(s)=baseᵢ+∫₀ˢvᵢ(t)dt`, and `vᵢ` is the actual supplied interval-integrable complex velocity. `Γ.closed` says `∫₀¹vᵢ=0`. The terminal sum counts every indexed curve occurrence.

The final source was independently compiled with Lean 4.34.0-rc2, warnings treated as errors: exit 0, 3.391 seconds, no output. SHA256 was stable before and after. Compilation imported existing baseline objects; I did not independently rebuild baseline dependencies or perform a full imported-axiom audit. `independent_primitive_compile.json` records the exact invocation and import path. First-seen SHA was `bdc7af002f15e5b904f11a76f459f048736be4d0210065d851533b14aa95095d`; final linter cleanup occurred during review, and this verdict concerns the final SHA above.

## Proof reconstruction

1. `ac_complex_primitive` projects `g : ℝ → ℂ` to its real and imaginary coordinates through bounded real linear maps. Both coordinates are interval integrable. Their primitive integrals are absolutely continuous by the pinned real theorem. Embedding these primitives in `ℂ` and adding `I` times the imaginary primitive preserves absolute continuity. For every `s ∈ [0,1]`, interval integrability on `0..s` follows by restriction; CLM commutation with integrals proves pointwise equality with the complex primitive. The coordinate transport is exact.
2. Adding the constant base proves every represented `Γ.curve i` absolutely continuous. Pinned Lebesgue differentiation proves its **real-variable complex derivative equals the actual velocity almost everywhere**. No smoothness or differentiability of the velocity is assumed.
3. The trace is a finite union of continuous images of compact `[0,1]`, hence compact. Holomorphicity on open `U` gives complex `C¹` regularity in ambient neighborhoods of every trace point, hence local Lipschitz control. The pinned compact local-to-global theorem supplies one Lipschitz constant on the complete trace, with no convexity or connectedness requirement.
4. Each curve maps the interval into that trace, so Lipschitz composition makes `F ∘ Γ.curve i` absolutely continuous. Holomorphicity also makes `deriv F` continuous on the trace, giving integrability of `vᵢ(s) • deriv F(γᵢ(s))` through the baseline line-integrand theorem.
5. Pinned `HasDerivAt.scomp` combines the complex derivative of `F` with the real derivative of `γᵢ`; its result is exactly `vᵢ • deriv F`. The difference between `F ∘ γᵢ` and the proposed integral primitive is absolutely continuous and has derivative zero almost everywhere. Pinned AC constancy therefore gives pointwise constancy, including endpoints.
6. At 0 the primitive integral is zero. Endpoint algebra gives the stated difference with the correct sign. `Γ.curve_one` and `Γ.curve_zero` identify both endpoints with the base. Every summand vanishes; finite summation gives the terminal theorem.

All leaves above were checked in the raw baseline sources or exact pinned Mathlib source. No circular dependence on the new cancellation theorem was found.

## Obligations

| Obligation | Result | Evidence |
|---|---|---|
| Real-coordinate transport to complex AC primitive | Passed | Integrable coordinate projections, real AC primitives, Lipschitz embeddings, exact CLM integral identities. |
| Holomorphic to Lipschitz on complete compact trace | Passed | Open-neighborhood `ContDiffAt`, local Lipschitz theorem, compact local-to-global theorem. |
| AC composition / trace containment | Passed | `MapsTo` is witnessed by the curve's own trace definition at every parameter value. |
| Chain rule almost everywhere | Passed | Scalar-tower `HasDerivAt.scomp` produces the actual velocity multiplication. |
| Endpoint differentiability failures | Passed | A.e. differentiation discards singleton endpoints; AC constancy restores equality at both endpoints. |
| Closure and sign | Passed | Primitive subtraction yields final minus initial value; both endpoints equal the base. |
| Arbitrary L¹ velocities | Passed | Includes discontinuous or unbounded representatives; only interval integrability is used. |
| Repeated / reversed / self-intersecting / stationary loops | Passed | Independent per-index cancellation; no geometric exclusions. |
| Zero count and empty trace | Passed | Empty sum is zero; compact union and hypotheses are vacuous. |
| Existence of a primitive for any holomorphic integrand | Out of scope | `F` is supplied; the integrated function is `deriv F`. |
| Banach-valued primitive theorem / full Cauchy or canonical-calculus theorem | Out of scope | The candidate states scalar exact-differential cancellation. |

## Safe use and remaining work

No gap was found in the audited claim. The strongest safe statement is cancellation of a scalar holomorphic exact derivative over every finite closed integrable-velocity cycle whose trace lies in the primitive's open domain. The theorem neither requires simple connectivity nor asserts primitive existence on an arbitrary domain. For example, it cannot be applied to `1/z` around the unit circle in an annulus without a single-valued holomorphic primitive.

The cheapest next check is full release-driver replay and imported-axiom inspection for this exact revision, followed by checking that every downstream application independently supplies the scalar primitive on the required trace neighborhood. Original rectifiable contour identification and broader canonical calculus obligations remain separately scoped.

## Provenance

Independent delegated source review under the already loaded `c20/proof-audit` instructions. Baseline definitions came from raw `ReleaseAnalyticContour.lean` and `ReleaseRectifiable.lean`, with hashes recorded in `PRIMITIVE_AUDIT.json`. Mathlib was pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The source paths and exact relevant theorem locators are recorded in that JSON.
