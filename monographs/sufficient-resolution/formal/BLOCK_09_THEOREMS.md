# Block 09 — Intrinsic metric obstruction and quantitative transport

**Komorebi P. · Sufficient Resolution v0.9.0 · 13 September 2026 (America/Chicago)**

61 new theorem declarations in six modules, 68 new explicitly named declarations.
Cumulative: 645 theorems, 53 modules, 773 named declarations. Supporting lemmas,
classical specializations, and boundary examples are included; these are not counts
of independent discoveries. The 47 predecessor proof files are unchanged.

## Contract and notation

Let A:G→V be a real linear map, δ:V→W a continuous real linear map, and δA=0.
V is a real inner-product space and W a real normed space. G need only be a real
module in the metric-quotient core. Put R=range A, K=ker δ, and H=K∩R⊥.
The positive results assume R and K admit orthogonal projection. Closed subspaces
of a Hilbert space and finite-dimensional local spaces provide the standard cases.
No finite-dimensional assumption or ambient completeness is imposed when projection
existence is supplied explicitly.

The quotient is the SAME `Globalization.ObstructionSpace A δ.toLinearMap` defined
in block 01: K divided by the realization submodule inside K. Its seminorm is the
standard Mathlib quotient seminorm. No custom replacement norm is declared.

### 1. Native quotient norm and linear isometry

`MetricObstruction.quotientToHarmonic_norm` proves

    ||quotientToHarmonic z|| = ||z||.

It uses the quotient's infimum-over-representatives property in one direction and
the norm bound on the canonical quotient map in the other. It does not assume
that the desired map is isometric.

`obstructionIsometry` upgrades the existing `obstructionEquivHarmonic` to

    K / range(A) ≃ₗᵢ[ℝ] K ∩ range(A)⊥.

`isometry_toLinearEquiv` proves the underlying equivalence is literally unchanged.
For compatible v and w, the checked norm and distance identities are

    ||[v]|| = ||(P_K-P_R)v|| = Metric.infDist v range(A),
    dist([v],[w]) = Metric.infDist (v-w) range(A).

The zero-norm test detects actual realizability under these hypotheses.
`compatibleRangeProjection` constructs the projection instance inside K, and
`quotient_inner_preserved` proves preservation of Mathlib's standard quotient inner
product when this instance is in scope. Distances are also preserved. This does
not define a separate metric to manufacture an isometry.

Principal names: `quotientToHarmonic_norm`, `obstructionIsometry`,
`norm_class_eq_infDist`, `distance_classes`, `quotient_norm_zero_iff`,
`norm_zero_iff_realizable`, `compatibleRangeProjection`, `quotient_inner_preserved`.

### 2. Unique minimum-norm compatible representative

`MetricRepresentatives.minimumRepresentative` is a linear section of the quotient
map, with range in the harmonic directions. `minimumSection` is its linear-isometry
bundling. For every class z, its selected representative s(z) satisfies

    [s(z)]=z,    ||s(z)||=||z||.

For every other compatible v representing z,

    ||v||² = ||z||² + ||v-s(z)||².

Thus s(z) is the unique compatible representative attaining the native quotient
norm; this is an actual ∃! theorem, not just an inequality or selected infimum.
The lift preserves class distances.

Principal names: `representative_error_energy`, `minimum_norm`,
`equal_norm_iff_minimum`, `unique_minimum_representative`, `representative_distance`.

Do not confuse this with block 08's minimum-norm GLOBAL SOURCE Bv. Here the
minimizer represents a LOCAL OBSTRUCTION CLASS, not an element of the source G.

### 3. Intrinsic obstruction for arbitrary, possibly inconsistent, data

`IntrinsicGlobalization.projectedClass` is the actual bounded map

    c(v)=[P_K v] : V → K/R.

It has norm at most one, so ||c(v)-c(w)||≤||v-w||. The old harmonic component is
its isometric representative. Writing i(v)=(I-P_K)v,

    dist(v,R)² = ||c(v)||² + ||i(v)||².

With σ>0 and σ||x||≤||δx|| on K⊥,

    dist(v,R)² ≤ ||c(v)||² + (||δv||/σ)².

In particular c(v)=0 alone does not guarantee v is realizable: δv=0 is also
required. The theorem `realizable_iff_class_and_residual_zero` proves exactly this.

With block 08's bounded canonical recovery B (actual complete/closed range of A),

    ||v-ABv||² = ||c(v)||² + ||i(v)||²,
    ||v-Ag||² = ||c(v)||² + ||i(v)||² + ||A(g-Bv)||².

Principal names: `projectedClass_opNorm_le`, `projectedClass_noise_bound`,
`intrinsic_distance_sq`, `intrinsic_conditioned_distance`,
`intrinsic_canonical_residual`, `intrinsic_candidate_total_error`.

### 4. Bounded transport on the existing obstruction quotients

A block-01 `Globalization.PresentationMap` f includes the realization and
compatibility commuting squares. It already induces the algebraic map fbar on
obstruction quotients. If its WHOLE local map satisfies ||f.localMap(v)||≤C||v||,
then the same induced map satisfies

    ||fbar(z)||≤C||z||,    dist(fbar(z),fbar(w))≤C dist(z,w).

`boundedObstructionMap` is this same map as a continuous linear map. For C≥0 its
operator norm is at most C. A harmonic realization formula is also checked.

A reverse presentation map g with bound M and gbar∘fbar=identity yields

    ||z||≤M||fbar(z)||.

With M>0, the two-sided bound is ||z||/M≤||fbar(z)||≤C||z||. Reverse-map existence
and its identity are explicit hypotheses, not inferred from forward continuity.
No arithmetic existence is smuggled into this linear presentation theorem.

Principal names: `obstructionMap_norm_le`, `boundedObstructionMap_opNorm`,
`harmonic_transport_formula`, `reverse_bound`, `two_sided_bound`.

### 5. Refinement as an actual quotient contraction

Fix K, its ambient metric, and R₀⊆R₁⊆K. `MetricRefinement.refinementMap` is the
actual induced map F:K/R₀→K/R₁. It is surjective and its composition law agrees
with repeated range enlargement. The metric results give ||Fz||≤||z||.
Let s₀(z) be the old canonical minimum representative. Then

    ||z||² = ||Fz||² + ||(P_R₁-P_R₀)s₀(z)||².

The lost quotient norm is exactly newly realizable information. There is no norm
loss iff this gain is zero. Fz=0 iff s₀(z) belongs to R₁. The result is not a
claim about arbitrary changes of metric, compatibility operator, or probability law.

Principal names: `refinementMap_surjective`, `refinementMap_comp`,
`refinementMap_norm_le`, `refinement_kernel`, `quotient_refinement_energy`,
`quotient_no_loss_iff`.

### 6. Nonclosed-range boundary for the native seminorm

For ANY submodule R of a real normed space, without a projection hypothesis,

    ||[v]||=0 iff v∈closure R,     [v]=0 iff v∈R.

Lean proves

    R not closed  ⇒  ∃ z≠0 with ||z||=0,
    (∀ z, ||z||=0 ⇒ z=0) iff R is closed.

Consequently a nonclosed quotient has no linear isometry EQUIVALENCE to a genuine
normed space. This is not a claim that a noninjective norm-preserving map out of a
seminormed space is impossible. Scalar zero-range and rescaling examples use the
actual quotient seminorm too.

Principal names: `zero_norm_iff_closure`, `class_zero_iff_membership`,
`nonclosed_nonzero_zero_norm`, `norm_detects_zero_iff_closed`,
`nonclosed_no_normed_isometry`, `scalar_rescaling_norm`.

## Exact rational evaluator: preserving the metric in nonorthogonal coordinates

Run

    python scripts/quotient_metric_certificate.py --input examples/quotient_metric_input.json --output certificate.json

For A(g)=(g,0,0), δ(x,y,z)=2z, v=(3,4,5), and compatible basis
b₁=(1,0,0), b₂=(1,2,0), the Gram matrix is [[1,1],[1,5]].
The compatible coordinates are (1,2), and the minimum class representative has
coordinates (-2,2), giving ambient vector (0,4,0). Its squared quotient norm is
16. Treating the coefficient coordinates as orthonormal gives the incorrect
squared value 4. The total reconstruction error is 41=16+25.

The evaluator checks the actual Gram metric, constrained minimization, normal
equations, and agreement with ambient projectors. The exact-rational suite uses
30 systems, 180 vectors, dimensions 0–5, seed 20260913, and 3,065 assertions.
It rejects 21 corrupt or invalid controls. The two calculation routes share
rational matrix helpers. The Python code/parser is not formally verified.

## Proof boundary and evidence

The core Hilbert quotient isometry is a classical mathematical structure, now
proved for the saved Komorebi quotient and integrated with its reconstruction,
transport, and refinement contracts. No novelty or priority certificate is implied.

See current VERIFICATION_SUMMARY.md and verification/release_v0.9.0/report.json.
Source code names above have the prefix Komorebi.SufficientResolution.
