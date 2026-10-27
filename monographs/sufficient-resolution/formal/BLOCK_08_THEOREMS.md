# Block 08 — Canonical minimum-norm global reconstruction

**Komorebi P. · 13 September 2026 (America/Chicago) · v0.8.0**

82 new theorem declarations and five definitions in six modules. Counts include
supporting lemmas and exact examples. They are not counts of independent discoveries.
The construction is the classical Moore–Penrose inverse, integrated with this
program's obstruction, compatibility, refinement, and reconstruction contracts.
No literature novelty claim is made for the inverse itself or its standard properties.

## Assumptions and construction

The explicit public constructor takes a bounded real linear map A:G->V between
Hilbert spaces and a proof that its ACTUAL range is closed. It does not replace
range(A) by closure(range(A)), assume A injective, or receive an inverse as input.

The core uses CompleteSpace G and CompleteSpace range(A). The local ambient V can
be an inner-product space without ambient completeness. The public closed-range
specialization assumes complete V so closedness supplies complete range(A).

Let N=ker(A), R=range(A), and S=N^perp. Restriction gives an actual bijective bounded
map A_S:S->R. Banach's open mapping theorem supplies a continuous inverse. Define

    B = inclusion_S * inverse(A_S) * P_R.

`MinimumNormReconstruction.restricted`, `restricted_injective`,
`restricted_surjective`, `restrictionEquiv`, and `recover` build these objects.
`ClosedRangeReconstruction.closedRecover` is the constructor with an explicit
closed-range proof. Its definition uses the core, not a different recovery map.

## 1. Exact projection and generalized-inverse identities

`image_recover`, `recover_image`, `image_comp_recover`, `recover_comp_image` prove

    A B = P_R,       B A = P_S.

`penrose_image` and `penrose_recover` prove

    A B A = A,       B A B = B.

`image_projection_symmetric` and `source_projection_symmetric` give the other
Penrose conditions in real inner-product symmetry form:

    <ABv,w> = <v,ABw>,       <BAg,h> = <g,BAh>.

These are not separately stated as equalities of Mathlib's adjoint operator.
`recover_kernel` and `recover_range` identify

    ker(B)=R^perp,       range(B)=N^perp.

`recover_projected_data` and `discarded_data_ignored` show that local components
orthogonal to actual realizations do not affect the selected source.
`recover_unique` proves that the best-image identity plus source orthogonality
uniquely determine the whole bounded linear recovery operator.

## 2. Exact optimality in the source, not just in the image

`MinimumNormOptimality.recover_best_error` and `recover_best` establish the actual
least-squares optimum using Metric.infDist to the actual range. For every candidate g,
`candidate_error_decomposition` proves

    ||v-A g||^2 = ||v-A Bv||^2 + ||A(g-Bv)||^2.

`all_least_squares_sources` characterizes ALL minimizers:

    ||v-A g|| = dist(v,R)   iff   g=Bv+k for some k in ker(A).

`source_norm_sq` proves, for every least-squares source,

    ||g||^2 = ||Bv||^2 + ||g-Bv||^2.

`minimum_norm`, `minimum_norm_unique`, and `unique_minimum_norm_least_squares`
therefore establish existence and uniqueness of the minimum-norm minimizer.
This is not uniqueness of every least-squares source when ker(A) is nonzero.

`exact_source_recovery_iff` and `unidentifiable_source_error` prove

    B(A g)=g iff g in N^perp,
    g-B(A g)=P_N g.

With noisy data A g+e, `noisy_source_error_sq` gives the exact orthogonal identity

    ||B(A g+e)-g||^2 = ||B e||^2 + ||P_N g||^2.

No statistical noise distribution is assumed: e is an arbitrary vector.

## 3. Source conditioning, noise, and approximate computational solutions

Use the existing `HilbertConditioning.CoerciveOffKernel A alpha` predicate:

    alpha ||g|| <= ||A g|| for g in N^perp,       alpha>0.

`SourceConditioning.exists_source_coercivity` obtains some such alpha from complete
range(A) using the bounded recovery. It includes A=0 and zero complementary spaces.
It does not claim the chosen alpha is optimal or uniform across models.

`recover_projected_bound`, `recover_bound`, and `recover_opNorm_bound` prove

    ||Bv|| <= ||P_R v||/alpha <= ||v||/alpha,       ||B|| <= 1/alpha.

`recover_noise_bound` and `recover_noise_projected_bound` give input perturbation
bounds, with the sharper version involving only P_R(v-w).
`identifiable_source_bound` estimates ||Bv-P_S g|| by ||v-A g||/alpha.

`noisy_source_bound_sq` retains the unidentifiable source term:

    ||B(A g+e)-g||^2 <= (||e||/alpha)^2 + ||P_N g||^2.

For g in N^perp, `noisy_identifiable_source_bound` yields ||B(A g+e)-g||<=||e||/alpha.

For an arbitrary candidate computed source g, `candidate_source_error_sq` and
`candidate_source_bound_sq` prove

    ||g-Bv||^2 = ||P_S g-Bv||^2 + ||P_N g||^2,
    ||g-Bv||^2 <= (||A g-P_R v||/alpha)^2 + ||P_N g||^2.

`candidate_tolerance_bound_sq` specializes to supplied whole-vector tolerances
||A g-P_R v||<=tau and ||P_N g||<=kappa. A small fit residual without a small kernel
component does NOT certify the minimum-norm source.

## 4. Closedness is characterized, not just assumed everywhere

`ClosedRangeReconstruction.closed_range_iff_coercivity` proves

    range(A) closed   iff   exists alpha>0, coercive off ker(A).

`bounded_recovery_iff_closed_range` proves the equivalent operator-level criterion

    [exists bounded B with B A = P_(ker A)^perp]   iff   range(A) closed.

The reverse implication does not assume the candidate B is the canonical inverse.
`nonclosed_no_bounded_recovery` records the nonclosed-range impossibility directly.
`finite_source_closed_range` and `finite_target_closed_range` supply closedness if
either ambient side is finite-dimensional. All inverse laws still allow rank zero.

## 5. Integration with the previous globalization block

Let delta:V->W be bounded with delta A=0, and K=ker(delta). Define the existing
components r=P_R v, o=(P_K-P_R)v, and i=(I-P_K)v. The module
`ReconstructionGlobalization` connects them to the ACTUAL constructed B:

    A Bv=r,       B o=0,       B i=0,       B(P_K v)=Bv.

`candidate_total_error_sq` gives, for every candidate global source,

    ||v-A g||^2 = ||o||^2+||i||^2+||A(g-Bv)||^2.

`canonical_conditioned_residual` and `two_condition_reconstruction` retain two
separate constants. With alpha conditioning A and sigma conditioning delta,

    ||Bv|| <= ||v||/alpha,
    ||v-A Bv||^2 <= ||o||^2+(||delta v||/sigma)^2.

There is no deduction of alpha from sigma. Compatibility does not establish source
identifiability or an inverse norm bound. `exact_realization_iff_components` identifies
A Bv=v exactly with vanishing obstruction AND vanishing inconsistency.

## 6. Exact Lean boundary examples

`ReconstructionExamples.scalar_recover` identifies B_c(v)=v/c for c nonzero.
For positive c, `scalar_recover_norm` proves exact equality ||B_c v||=||v||/c,
so the source bound is attained. `scalar_coercivity` verifies its whole-map premise.
`arbitrarily_small_data_unit_source` and `no_uniform_source_conditioning` prove
arbitrarily small data can require a unit recovered source across changing maps,
and no common inverse-sensitivity constant covers all nonzero scalar maps.

For the zero map, `zero_map_recovery`, `zero_map_every_source_best`, and
`zero_map_not_full_source_recovery` distinguish the canonical zero selection from
recovery of every original source. These are universal real statements, not tests.

## 7. Rational executable and tests

    python scripts/reconstruction_certificate.py --input examples/reconstruction_input.json --output certificate.json
    python scripts/check_reconstruction.py

The executable constructs B using a rational basis J of range(A^T):

    B=J ((A J)^T(A J))^-1 (A J)^T.

It checks all four Penrose identities and the exact positive-semidefinite witness
A^T A-alpha_squared*P_S >=0. It does not use a floating singular value. Automatic
alpha_squared is the reciprocal of ||B||_F^2, with alpha_squared=1 for B=0.
A user-supplied value is verified rather than accepted as an assertion.

The example A=[[1,1],[0,0],[0,0]], delta=[[0,0,2]], v=[3,4,5] gives

    Bv=[3/2,3/2], ||Bv||^2=9/2, local error^2=41=16+25,
    alpha_squared=2, sigma_squared=4.

The alternative source [3,0] has the same best image but contains kernel ambiguity
of squared norm 9/2. Its squared norm is 9, not the minimum 9/2.

Controls use seed 20260913, dimensions 0..6, 49 systems and 343 vectors:
4,828 exact assertions, 58 rejected malformed/corrupted inputs, 49 alternative
rank-factorization comparisons, and 16 exact SymPy pseudoinverse comparisons.
The algorithm, parser, PSD checker and arbitrary JSON certificates are NOT Lean-
verified. Mathematical theorems are separate kernel-checked declarations.

## 8. Boundaries retained

Real Hilbert/inner-product spaces and known bounded linear maps only. Actual closed
range (or the core's complete-range hypothesis) cannot be replaced by density.
Source recovery is modulo ker(A), unless source identifiability is supplied.
These results do not establish optimal regularization, approximate rank stability,
positive or integral feasibility, arithmetic existence, or data-driven operator
identification. A nonclosed-range conditional impossibility theorem is proved;
this block does not build a concrete nonclosed-range Hilbert operator example.
The harmonic obstruction quotient remains linearly identified, not isometrically
identified, in the inherited code. No formal Python extraction or independent
proof-kernel implementation is claimed.
