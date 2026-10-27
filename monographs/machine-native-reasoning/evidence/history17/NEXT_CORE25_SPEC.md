# Exact restart after Core 2.4

The next source target is **Core 2.5**, `r:positive-packets`, in the unchanged
`source/core_v0.2.tex`, with the cone and mass setup immediately preceding the
proposition. Complete both the general cone-mixture theorem and the coordinate
classification before changing its formal status. Core 3.2 follows it.

## General cone sector

Use a real vector space, a convex cone, a linear mass functional strictly positive
on every nonzero member of the cone, and a finite complete family of linear maps
preserving that cone. A normalized input lies in the cone and has mass one.

Construct each packet, its mass, and each positive-mass normalized component.
Prove nonnegative weights, total weight one, zero weight implying a zero packet,
membership and unit mass for each normalized positive component, and exact
weighted reconstruction over only the positive weights. Do not require idempotence
for this sector, assume positivity of arbitrary coordinates, or silently replace
strict positivity by mere nonnegativity. State the treatment of zero weights
explicitly rather than treating division by zero as a probability definition.

The pinned Mathlib source has `ConvexCone` and its positive-scalar `smul_mem` in
`Mathlib/Geometry/Convex/Cone/Basic.lean`. This is a locally inspected API pointer,
not a claim that a draft using it has compiled. Its positive-scalar convention
fits normalization of nonzero packets. Zero packets are handled by linearity.

## Coordinate classification sector

For the standard nonnegative cone on finite real coordinate vectors, prove that
cone preservation is equivalent to entrywise nonnegative matrix coefficients.
Completeness makes every off-diagonal entry zero. With idempotence, each diagonal
coefficient is either zero or one. The diagonal sums prove that every coordinate
is selected by exactly one member. Derive disjointness rather than assuming it.
Tie this actual matrix classification back to the original linear maps. Handle
zero-dimensional and empty-family edge cases without unnecessary assumptions.

`Finset.sum_eq_zero_iff_of_nonneg` exists in the pinned ordered-big-operator
sources and is a candidate for the off-diagonal argument. No new formal result
is attributed to this lookup.

## Required boundary examples and rejection controls

Use exact rational or real examples for a signed Haar detail with zero mass,
a non-strict mass functional that annihilates a nonzero positive vector,
the two complete positive half-identity maps that are not idempotent, and an
invertible coordinate change transporting the cone to one with negative
coordinates. Omitting completeness must fail the unit-total-weight conclusion.
These examples distinguish cone membership from the visible signs of coordinates.

## Acceptance

Preserve all existing substantive modules and source-book files. Add source-facing
APIs and expected mathematical rejection controls. Complete cumulative cold
builds, actual transitive axiom audits, own-kernel replays, imported-cache hash
checks and a separately extracted-source rebuild. Do not count Core 2.5 as
formalized until the entire source scope and the complete gates pass.

Core 3.2 is the final selected target after that: signatures for exactly the
partition-generated evidence algebra, their occupancy bijection, all attainable
cell/target pairs, exactly 2^r signatures, and the r-bit necessity and sufficiency.
The quantification over all candidate subsets and the exact evidence-algebra
premise must be retained.
