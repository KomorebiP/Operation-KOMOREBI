# Independent general Cauchy comparison audit

**Verdict: proved as written.** Main source: `dixon/ReleaseCycleCauchy.lean`, SHA256 `dcffa6777c08ef6efcea05a01701c27cdf9cb18f9b17133709ff1dbcc176febc`. I made no source edits. Full source hashes, dependency graph and obligation matrix are in `CAUCHY_AUDIT.json`.

The exact normalized claim is: for any complex Banach target `E` with the stated compatible real scalar structure, any two finite closed actual integrable-velocity cycles `Γ, Δ`, any open `U ⊆ ℂ` containing both complete traces, and any `f : ℂ → E` complex differentiable on `U`,

\[
(\forall w\notin U,\ \operatorname{wind}_\Gamma(w)=\operatorname{wind}_\Delta(w))
\Longrightarrow
\Gamma.\operatorname{lineIntegral}(f)=\Delta.\operatorname{lineIntegral}(f).
\]

`U` may be disconnected, nonconvex, unbounded, empty or all of `ℂ`. Targets may be zero-dimensional or infinite-dimensional. Cycles may contain constants, reversals, repeated loops, self intersections or no entries. No curve `C¹` or pointwise velocity bound is assumed.

The winding in this theorem is exactly the complex-valued normalized analytic integral `(2πi)⁻¹ Γ.lineIntegral (fun z => (z-w)⁻¹)`. It is used geometrically off the trace; points outside `U` are automatically off both traces. The argument uses no winding-integrality certificate or supplied Cauchy conclusion.

## Actual objects

An `IntegralCycle` consists of a finite count, bases, arbitrary complex velocities `vᵢ : ℝ → ℂ` interval integrable on `[0,1]`, and `∫₀¹vᵢ=0`. Its curve is `γᵢ(s)=baseᵢ+∫₀ˢvᵢ`; its line integral is `Σᵢ∫₀¹vᵢ(s) • f(γᵢ(s)) ds`.

For the continuation, `H1Γ(w)=Γ.lineIntegral(dslope f w)` and `H2Γ(w)=Γ.lineIntegral(fun z => (z-w)⁻¹ • f z)`. The divided difference is `(z-w)⁻¹ • (f z-f w)` off the diagonal and `deriv f w` on it. `pairDixon` equals `H1Γ-H1Δ` inside `U` and `H2Γ-H2Δ` outside.

## Dependency reconstruction

1. **Parameter differentiation.** The source applies the exact pinned dominated-derivative interval-integral theorem to the actual integrands. A uniform derivative-density bound `M` becomes the integrable dominating function `‖vᵢ(t)‖ M`. Near-parameter measurability, base-parameter integrability, derivative-density measurability, pointwise derivative formulas and domination are all supplied. It requires no bounded velocity.
2. **H1.** Joint continuity of divided differences on arbitrary open domains is proved explicitly: locally convex integral representation near diagonal points and a quotient argument away from the diagonal. Pinned removable-singularity holomorphy controls fixed-node divided differences including the diagonal. Compact trace times a closed parameter ball bounds the divided difference; a Cauchy derivative estimate gives the uniform derivative bound needed in step 1. The repeated-divided-difference identity supplies derivative continuity in the trace variable. The resulting cycle transform is holomorphic on `U`. No standalone two-variable complex-differentiability theorem is asserted or needed.
3. **H2.** A compact trace admits one positive separation bound from a small parameter ball about each off-trace point. The derivative in `w` of `(z-w)⁻¹` is **positive** `(z-w)⁻²`. Compact bounds for `f` and the inverse-square kernel give step 1's domination. At infinity, reverse triangle inequality gives `‖H2Γ(w)‖ ≤ Γ.length M/(‖w‖-R)`; compactness supplies `R,M`, so H2 tends to zero along the cocompact filter.
4. **Winding.** Kernel differentiation gives a derivative proportional to the inverse-square integral. The latter vanishes because it is the scalar exact derivative of `-(z-w)⁻¹`, using the independently audited primitive theorem. Zero derivative on an off-trace ball makes winding locally constant. Far from a ball containing the trace, `(z-w)⁻¹` has a primitive on that ball by the exact pinned `DifferentiableOn.isExactOn_ball`; scalar cancellation makes winding **exactly zero** there. This step is independent of the new general comparison theorem.
5. **Matching.** Off the trace, direct divided-difference algebra gives `H1Γ(w)=H2Γ(w)-KΓ(w) • f(w)`, where `KΓ` is the unnormalized inverse-kernel integral. Equal winding implies equal `K` by cancellation of the nonzero Cauchy prefactor. Subtracting the two identities gives `pairH1H2match`.
6. **Piecewise glue.** At a point inside `U`, the continuation locally equals the H1 difference. At a point `w` outside `U`, both traces avoid it. On one common neighborhood, both traces are avoided and each winding is constant at its value at `w`. Thus nearby `a` satisfies `windΓ(a)=windΓ(w)=windΔ(w)=windΔ(a)`. If `a∈U`, matching identifies the H1 branch with H2; otherwise equality is definitional. Hence at every outside point, including every boundary point, the continuation locally agrees with the holomorphic H2 difference. It is entire.
7. **Liouville.** Eventually both windings are zero and both traces are avoided. Matching then identifies the continuation with the H2 difference even at large parameters lying in unbounded `U`. Its limit at infinity is zero. The exact pinned Banach-valued Liouville theorem makes the continuation zero everywhere. Its `Nontrivial` hypothesis concerns the domain `ℂ`, so no nonzero target vector is required.
8. **Twist extraction.** For a chosen `w∈U`, apply the concrete zero-continuation theorem to `g(z)=(z-w) • f(z)`. For `z≠w`, `dslope g w z=f(z)` by cancellation. At `z=w`, product differentiation gives `1 • f(w)+0 • f'(w)=f(w)`. Thus the identity holds on either trace even when `w` itself lies on a trace. The U-branch at `w` becomes the difference of the original line integrals.

Every input of the conditional helper `pairDixon_eq_zero_of_pieces` is supplied in the concrete `pairDixon_eq_zero`: `pairH1H2match`, both eventual winding-zero/off-trace inputs, and both H2 decay limits. The final theorem has none of these as extra assumptions.

## Obligation matrix

| Obligation | Result | Decisive point |
|---|---|---|
| Genuine arbitrary L¹ velocities | Passed | Constant times integrable velocity norm is the dominator. |
| H1 diagonal and arbitrary open U | Passed | Local diagonal ball; off-diagonal quotient; exact fixed-node removable-singularity theorem. |
| H1 compact uniform derivative control | Passed | Compact product bound plus Cauchy derivative estimate; no finite-dimensional target assumption. |
| H2 off-trace derivative and decay | Passed | Uniform positive separation and reciprocal norm bound. |
| Winding local constancy / eventual zero | Passed | Scalar primitive cancellation; no integrality or circular use of general comparison. |
| Boundary glue | Passed | Explicit common off-trace neighborhood and transported winding equality. |
| Concrete discharge of helper hypotheses | Passed | Every analytic/matching/infinity leaf appears in `pairDixon_eq_zero`. |
| Trace-point twist extraction | Passed | Diagonal product derivative is included explicitly. |
| Empty U | Passed | Separate norm-by-zero branch; no point is selected from empty U. |
| Zero count / constants / repeated or reversed loops | Passed | Finite sums and per-curve proofs impose no exclusions. |
| Zero-dimensional or infinite-dimensional E | Passed | Compatible complex Banach structure suffices; Liouville's nontrivial domain is `ℂ`. |
| Winding integrality / original RS contour transport / canonical HFC | Out of scope | Separate representation and calculus bridges. |
| Fresh full dependency build / imported-axiom audit | Not addressed | Fresh main compilation imports existing dependency objects. |

## Compiler and source checks

The reviewer independently executed the pinned Lean 4.34.0-rc2 compiler on the main source with strict warnings and auto-implicit restrictions: **exit 0**, no output, **3.515 seconds**. Its SHA256 was stable before and after. `independent_cauchy_compile.json` records the exact command and search path. Imports came from existing `cauchy/objects`, `primitive`, and analytic baseline objects; this is a fresh main-source check, not a new full dependency rebuild.

Pinned Mathlib sources inspected include `ParametricIntervalIntegral.lean:97–112`, `DSlope.lean:35–46`, `RemovableSingularity.lean:60–65`, `HasPrimitives.lean:116,291–293`, `MeanValue.lean:767–771`, and `Liouville.lean:131–152`. Mathlib revision is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The primitive dependency's final SHA matches the previously independently audited primitive source. An isolated child reviewed the H1/H2 sources independently; its report is under `h1_h2/`.

## Remaining scope

No gap was found for `lineIntegral_eq_of_winding` under its actual hypotheses. The strongest safe statement is the general Banach-valued comparison stated above, for the explicit normalized analytic winding and actual Bochner cycle integrals. The cheapest next check is full release-driver replay and imported-axiom inspection of the frozen tree, followed by the separately scoped canonical-HFC and original-contour identification checks.
