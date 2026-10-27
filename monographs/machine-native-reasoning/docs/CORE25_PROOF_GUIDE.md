# Core 2.5 — proof guide and correspondence

## Source and mathematical types

The immutable anchor is `source/core_v0.2.tex`, label `r:positive-packets`, original
printed page 6 and its setup immediately preceding the statement. The exact source
index and bindings are retained. The manuscript treats a real vector space, a
convex cone K, a linear mass λ strictly positive on K \ {0}, and a finite complete
family of linear packet operators preserving K.

`ConvexCone ℝ V` supplies actual closure under addition and positive scalar
multiplication. Its library definition does not force nonemptiness or zero
membership. This is sufficient: a normalized input is separately required to
belong to the cone; normalization uses a strictly positive inverse scalar. Thus no
extra pointedness, closedness, finite-dimensionality or coordinate positivity is
silently added. Strict mass already rules out nonzero zero-mass cone members.

## The general mixture

`StrictMass C mass` is exactly positivity on nonzero cone members.
`Preserves C P` checks actual image membership, not a name or intended property.
`Complete P` is equality of the finite sum of the supplied operators with the
identity. `IsState C mass v` asserts both cone membership and mass one.

For each index i, `weight mass P v i = mass (P i v)`. Cone preservation and strict
mass prove nonnegativity, and zero weight is equivalent to the zero packet.
Linearity carries completeness to the sum-of-weights identity. The positive index
subtype contains exactly the normalizable packets. Scaling by the inverse weight
preserves the cone and gives mass one. Multiplication by the original weight
recovers the packet. Finally the omitted terms vanish, so the restricted sum still
reconstructs v and its weights still sum to one.

Principal endpoint: `Komorebi.MachineTheory.PositivePackets.source_core25`.
The separate endpoint `sum_positive_weights_one` states the active-weight sum.
No idempotence or orthogonality appears in this sector. Positive halves of the
identity form a checked complete mixture even though neither half is idempotent.

## Coordinate classification

`Coordinate.cone N` is the actual coordinatewise nonnegative cone on `N → ℝ`.
`coefficient P r c` is obtained by applying P to the standard basis vector at c,
then evaluating coordinate r. `basis_expansion` and `coordinate_action` establish
the link to an arbitrary vector, rather than assuming a matrix representation.

Preserving the cone is equivalent to every coefficient being nonnegative.
Completeness says the coefficient sums are those of the identity. Nonnegative
terms summing to zero force all off-diagonal entries to vanish. Hence each map is
diagonal. Its idempotence then makes each diagonal coefficient d satisfy d²=d,
and the real-field identity implies d=0 or d=1. The diagonal sum being one gives
exactly one owner for every coordinate. The constructed owner map represents the
original operators as coordinate selectors. Different owners have disjoint ranges
and their cross compositions are zero.

`source_core25_coordinate` returns that concrete representation, unique ownership
and disjoint composition. `classification_iff` also proves every such selector
family is positive, complete and idempotent. Thus the result is a characterization,
not only a necessary condition. No positive coordinate dimension, nonempty index
type, pairwise-orthogonal assumption, or surjective ownership assumption is added.
An index may own no coordinates and represent the zero operator.

## Coordinate changes

For a linear equivalence e, `Transport` pushes the cone forward, pulls the mass
back by e⁻¹, and conjugates the packet maps. It proves preserved state membership,
strict mass, completeness, idempotence where supplied, equality of weights, and
equality of normalized packets after applying e. `source_coordinate_change`
collects the hypotheses needed to apply the general mixture theorem in the new
coordinates. It is not a theorem that signed coordinates are valid in the old
coordinate cone with the old mass left unchanged.

A real shear sends a normalized nonnegative state to (-1,1). It belongs to the
transported cone and has unit transported mass, despite its negative first
coordinate. The Haar detail example is different: it remains outside the declared
positive cone and has zero mass without vanishing. Coordinate signs alone cannot
replace the cone and mass contract.

## Source-facing checks and boundaries

`checks/CheckPositivePacketsAPI.lean` checks the source theorem from raw linear
maps, pointwise membership hypotheses, actual operator-sum equality and normalized
input. It independently checks the coordinate result from raw nonnegative inputs,
without assuming the bundled definitions as conclusions.

Eleven negative fixtures test omitted strict mass, omitted cone preservation,
omitted completeness, nonunit input, zero-packet normalization, non-idempotent
positive halves, overlapping projectors, incorrect coordinate-sign inference and
an unchanged mass after coordinate transport. They must fail for the expected
proof diagnostics, not name-resolution errors, missing imports or timeouts.

These declarations establish mathematical constructions. Some use classical choice
and are noncomputable. They do not certify a learned representation, numerical
stability, a physical probability model, or the Python checker in all executions.
The standard axioms and recorded Lean/dependency environment remain trusted.
