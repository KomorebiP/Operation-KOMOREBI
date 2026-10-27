# Block 07 — Orthogonal globalization, obstruction, and conditioning

**Komorebi P. · 13 September 2026 · v0.7.0**

76 new theorem/lemma declarations, 10 definitions, six production modules.
These counts include supporting lemmas and examples, not independent discoveries.
See VERIFICATION_SUMMARY.md for the actual cumulative build and replay status.

## 1. Actual orthogonal components

Let V be a real inner-product space. Let R <= K be subspaces admitting orthogonal
projections P_R and P_K. Define continuous linear maps

    r(v) = P_R v,
    o(v) = (P_K-P_R)v,
    i(v) = (I-P_K)v.

The source constructs these maps from Mathlib's actual orthogonal projections.
They are not supplied as unspecified vectors satisfying the desired conclusion.

`OrthogonalResolution.obstruction_mem`, `inconsistency_mem`, `components_sum`,
`unique_components`, and `obstruction_range` prove

    r(v) in R, o(v) in K intersect R^perp, i(v) in K^perp,
    v = r(v)+o(v)+i(v),
    range(o) = K intersect R^perp.

The three terms are pairwise orthogonal and form the unique such decomposition.
`norm_sq_components` and `error_norm_sq` give

    ||v||^2 = ||r(v)||^2 + ||o(v)||^2 + ||i(v)||^2,
    ||v-r(v)||^2 = ||o(v)||^2 + ||i(v)||^2.

For every candidate u in R, `candidate_error_sq` proves

    ||v-u||^2 = ||v-r(v)||^2 + ||r(v)-u||^2.

`best_approximation_unique` identifies the unique nearest represented vector.
`infDist_eq_error` and `infDist_sq_decomposition` use Metric.infDist, not a new
quantity simply defined to equal the proposed answer:

    dist(v,R)^2 = ||o(v)||^2 + ||i(v)||^2.

The three component maps are nonexpansive in the norm, including their responses
to perturbations of v (`*_noise_bound`). These results need projectability, not
finite dimension. Closed subspaces of a Hilbert space and finite-dimensional
subspaces supply it.

## 2. Connection with the original obstruction quotient

Let A:G -> V be linear and delta:V -> W continuous linear, with delta A=0.
Set R=range A, K=ker delta. Assume their projections exist.

`HilbertGlobalization.obstructionEquivHarmonic` constructs the actual equivalence

    (ker delta)/(range A inside ker delta)  ~=  ker delta intersect (range A)^perp.

The left side is the existing block-01 `Globalization.ObstructionSpace`, not a
new quotient with altered definitions. `quotientToHarmonic`, `harmonicToQuotient`,
`harmonic_roundtrip`, and `quotient_roundtrip` supply both maps and inverse laws.

For compatible v, `class_zero_iff_component_zero` identifies class vanishing with
vanishing of o(v). `same_class_iff_same_harmonic` identifies equality of classes.

This is a LINEAR equivalence. No quotient-norm isometry is asserted by this block.

`exists_best_global_image` proves the projected vector is actually A(g) for some g.
`best_global_image_unique` characterizes best images, without assuming A injective.
Uniqueness of the global source g is separately proved only with injectivity.

## 3. Residual-to-error bounds retain both obstruction and conditioning

For sigma>0, `HilbertConditioning.CoerciveOffKernel delta sigma` means

    sigma ||x|| <= ||delta x|| for every x in (ker delta)^perp.

`inconsistency_residual` and `inconsistency_le_residual` prove

    delta i(v) = delta v,
    ||i(v)|| <= ||delta v||/sigma.

For R<=ker delta, `conditioned_distance_sq` gives

    dist(v,R)^2 <= ||o(v)||^2 + (||delta v||/sigma)^2.

`obstruction_lower_bound` gives ||o(v)||<=dist(v,R), while
`compatible_distance` gives dist(v,R)=||o(v)|| when delta v=0.

Given ||o(v)||<=eta and ||delta v||<=epsilon, the tolerance theorems give

    dist(v,R)^2 <= eta^2 + (epsilon/sigma)^2,
    dist(v,R) <= eta + epsilon/sigma.

Nonnegativity of eta and epsilon follows from these norm hypotheses. Sigma must
be strictly positive. A residual-only estimate requires o(v)=0 or R=ker delta.

## 4. Finite dimension closes the existence obligation

`exists_coercivity_finite` proves that some sigma>0 exists when dim V is finite.
It restricts delta to (ker delta)^perp, proves injectivity, and uses finite-dimensional
anti-Lipschitz control. The zero-complement case is included.

It does NOT compute a smallest positive singular value or a uniform family-wide
constant. No singular-value assumption is silently manufactured.

`FiniteGlobalization.finite_conditioned_globalization` produces a sigma, its
whole-map coercivity proof, and for every v an actual g with A(g)=P_R(v), the exact
error split, and the conditioned upper bound.

`finite_residual_bound_iff_exact` proves the stronger characterization

    [exists c>0, forall v, dist(v,range A)<=c||delta v||]
       iff range A = ker delta,

under delta A=0 and finite-dimensional V.

`closed_range_best_global` and `closed_range_zero_distance_iff_realizable` extend
nearest-image existence and zero-distance realization to complete V with the
explicit hypothesis that range A is closed. Closure is not substituted for range.

## 5. Exact accounting for enlargement of the realizable space

For R0<=R1<=K, with the compatibility space K held fixed, define

    gain(v)=(P_R1-P_R0)v.

`GlobalizationRefinement.obstruction_refinement_sq` and `distance_refinement_sq` prove

    ||o0(v)||^2 = ||o1(v)||^2 + ||gain(v)||^2,
    dist(v,R0)^2 = dist(v,R1)^2 + ||gain(v)||^2.

`no_gain_iff_equal_distance` characterizes equality by gain(v)=0.
This is enlargement of the realized subspace, NOT a claim about every arbitrary
change of packetization, metric, or compatibility tests.

`obstruction_invariant_realizable_shift` proves o(v+r)=o(v) for r in R.
`inconsistency_invariant_compatible_shift` proves i(v+k)=i(v) for k in K.

## 6. Universal exact boundary examples

`GlobalizationExamples.pure_obstruction` and
`zero_residual_cannot_bound_obstruction` use R=0, K=R, v=1. The compatibility
residual is zero, but the global reconstruction distance is one. No residual-only
bound can cover this model.

The actual bounded scalar compatibility operator delta_s(x)=s*x has kernel zero
for s!=0. For s>0, sigma=s is a valid coercivity constant, and the distance bound
is attained at v=1. The residual equals s while the distance to range(A)=0 is one.

`arbitrarily_small_residual_unit_error` proves this for every positive epsilon.
`no_uniform_conditioning_over_scalar_family` proves that no fixed c>=0 bounds
distance by c times residual over all these exact scalar presentations.

These are Lean-proved real statements, not finite numerical observations.

## Rational evaluator example (separate implementation evidence)

A(g)=(g,0,0), delta(x,y,z)=2z, v=(3,4,5) gives

    realized=(3,0,0), obstruction=(0,4,0), inconsistency=(0,0,5),
    error_squared=41=16+25,
    residual_squared=100, sigma_squared=4,
    conditioned_bound_squared=16+100/4=41.

The evaluator computes rational orthogonal projectors and a global preimage.
Its coercivity certificate checks positive semidefiniteness of

    delta^T delta - sigma_squared P_inconsistency

by exact rational Schur complements. The checker is tested, not itself proved in
Lean. General Lean theorems and finite Python implementation checks remain distinct.

## Boundaries

No positivity, probability, integrality, nonlinear descent, arithmetic existence,
or global Langlands correspondence follows. A global source norm is not required
in the abstract theorem; consequently this block does not construct a minimum-norm
global preimage or bound its norm. Those require additional source-space structure
and conditioning of A, distinct from conditioning of delta.
