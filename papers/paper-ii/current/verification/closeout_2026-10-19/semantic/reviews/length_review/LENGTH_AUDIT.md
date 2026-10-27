# Independent audit of the Paper II length bridge

**Verdict: proved as written**, for `ReleaseRectifiableLength.lean` SHA256 `30e78d1e2f26885613d4c7a1057617be05e68a157dcfc6febbdad9e9f48c7a55`. This verdict covers the four candidate declarations ending in `length_cycleOfRectifiable_le`, not the whole Paper II closeout. I made no source edits.

The normalized claim is: for every finite family `f : Fin n → ℝ → ℂ` of continuous BV paths on `[0,1]` with `fᵢ(1)=fᵢ(0)`, the constructed integral cycle satisfies

\[\sum_i\int_0^1\|v_{g_i}(s)\|\,ds\leq\sum_i\operatorname{Var}_{[0,1]}(f_i),\qquad g_i=\texttt{unitIntervalPath}(f_i).\]

The first-seen file had hash `a865a03c7fd9d8ccb02832de6736e40d8664e76726adfe3a5f0b55f9a16b8006`; another owner revised it during review. The final hash above was read and independently compiled with hash stability before/after. The compiler accepted it with warnings treated as errors, exit 0, in 2.48 seconds. The invocation imported previously compiled baseline objects; I did not independently rebuild those dependencies or run a complete axiom audit. Full command, environment search path and output are in `independent_length_compile.json`.

## Objects reconstructed from the raw definitions

| Object | Exact type / meaning |
|---|---|
| `coordinateVelocity` | `(ℝ → ℂ) → ℝ → ℂ`; `ofReal(deriv (Re ∘ f) x) + ofReal(deriv (Im ∘ f) x) * I`. Each absent coordinate derivative defaults to zero. |
| `geometricLength` | `(ℝ → ℂ) → ℝ`; `(eVariationOn f (Icc 0 1)).toReal`. `hv` guarantees finiteness. The variation is the supremum of ordered finite sums of genuine complex Euclidean distances. |
| `unitIntervalPath` | `(ℝ → ℂ) → ℝ → ℂ`; `naturalParameterization f [0,1] 0 (geometricLength f * s)`. The natural parameterization uses `Function.invFunOn` of cumulative variation. |
| `IntegralCycle.length` | `IntegralCycle → ℝ`; `Σ i : Fin Γ.count, ∫₀¹ ‖Γ.velocity i s‖ ds`. For this constructed cycle its velocities are exactly the coordinate velocities of `unitIntervalPath fᵢ`. |

`coordinateVelocity` is the genuine real-variable complex derivative whenever both coordinates are differentiable. It can differ from `deriv f` at other points: `f(t)=t+i|t|` gives coordinate velocity 1 at 0 while the nonexistent complex-valued real derivative defaults to 0. The candidate handles this distinction correctly.

## Dependency reconstruction

1. Complex `K`-Lipschitz control gives separate real and imaginary coordinate `K`-Lipschitz control by `abs_re_le_norm` and `abs_im_le_norm`.
2. If both coordinate derivatives exist, coordinate recombination gives `HasDerivAt f (coordinateVelocity f x) x`, and pinned `HasDerivAt.le_of_lipschitzOn` bounds its norm by `K`.
3. If a coordinate is not differentiable, its `deriv` is zero; the other coordinate's norm is bounded by pinned `norm_deriv_le_of_lipschitzOn`. This proves the norm bound at **every interior point**, without a Rademacher premise.
4. Lipschitz control yields absolute continuity and baseline `integrable_coordinateVelocity`; pinned `integral_mono_on_of_le_Ioo` converts the interior bound into `∫ₐᵇ ‖v‖ ≤ (b-a)K` under Lebesgue measure.
5. Baseline `unitIntervalPath_lipschitz` supplies `K=geometricLength fᵢ`. Instantiation on `[0,1]` and finite summation yield the advertised inequality.

There is no circular use of a length/speed equality or of the final contour estimate.

## Coverage and boundary checks

| Obligation | Result | Decisive reason |
|---|---|---|
| Every continuous BV closed path on normalized `[0,1]` | Passed | These are exactly `hv`, `hc`, `hclosed`; no smoothness/injectivity assumptions. |
| Empty family `n=0` | Passed | Both sums are zero. |
| Constant / zero-length paths | Passed | `K=0` is allowed; `unitIntervalPath f s=arcPath f 0` for all `s`; no division by length. |
| Repeated loops / retracing / self intersections | Passed | Every `Fin n` occurrence is summed; ordered metric variation counts traveled multiplicity. |
| Singular continuous original parameterization | Passed | Only the constructed Lipschitz path is differentiated. |
| One or both coordinate nondifferentiabilities | Passed | Explicit `deriv=0` case splits. |
| Endpoints / arbitrary outside extension | Passed | Bound is required only on `Ioo`; interval-integral monotonicity removes endpoint singletons. |
| Intermediate degenerate interval `a=b` | Passed | Empty interior, zero interval integral, zero right side. |
| Exact equality of geometric and velocity length | Not addressed | The theorem asserts only the sufficient upper bound. |
| Original oriented contour integral equality | Out of scope | Trace equality alone does not establish oriented integral equality. |
| Canonical calculus / winding / independence | Out of scope | Separate bridge obligations. |

## Exact original-length consequence

Directly proved is `L_velocity(cycleOfRectifiable f) ≤ Σᵢ geometricLength(fᵢ)`. Combined with any estimate `‖A‖ ≤ L_velocity * B` and `0 ≤ B`, it yields `‖A‖ ≤ (Σᵢ geometricLength(fᵢ))*B`. For the existing chosen-cycle defect estimate, the multiplier is `(2π)⁻¹ Mh ‖continuousDefect‖ Mc Mf`, whose nonnegativity follows from the existing nonnegative uniform-bound hypotheses.

For a generic line integral, the same substitution is valid with `M ≥ 0` and the existing trace bound; baseline trace preservation transfers that bound from original paths. The candidate itself does not state this combined corollary. It also does not identify original classical contour integrals with constructed velocity integrals, or identify those integrals with canonical holomorphic calculus.

No gap was found for the audited length claim. The strongest safe statement is the finite-family upper bound above, counting multiplicity. The next check is full-driver replay of this exact final revision and independent verification of the downstream monotonicity and contour/canonical bridges.

## Provenance

Independent delegated source review using `c20/proof-audit`; no project `AGENTS.md` or `.mathbox` ledger was found. The skill's referenced obligation checklist resource was unavailable at the resolved locators, so the relevant type, domain and boundary obligations were applied directly. Raw baseline source hashes and pinned Mathlib theorem locators are recorded in `LENGTH_AUDIT.json`. Source inspection used Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`; the candidate was checked with Lean `4.34.0-rc2`.
