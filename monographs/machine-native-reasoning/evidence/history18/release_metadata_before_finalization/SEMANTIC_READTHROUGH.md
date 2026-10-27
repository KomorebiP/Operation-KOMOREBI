# Semantic read-through of the new Core 2.5 block

This record describes source-facing checks performed in this continuation. It is
not independent peer review and does not itself certify successful Lean execution.
The completed gate receipts, if admitted, are the formal execution evidence.

## Preservation of the mathematical target

The original source proposition has two distinct clauses. The first gives a
finite mixture on a real cone with a strictly positive linear mass. The second
classifies complete positive idempotent maps on the coordinate cone. These clauses
have different hypotheses and are not collapsed into a single coordinate theorem.
The raw API re-states both without assuming the conclusions as bundled data.

The coordinate endpoint does not mention the mass functional because its
classification needs only cone preservation, completeness and idempotence. Removing
an unused mass assumption proves a stronger operator statement that still supplies
the original source clause. Conversely, the general mixture endpoint does not add
idempotence, finite dimension, a coordinate basis or a positive-coordinate condition.

## Zero weights and finite sums

A normalized state has a nonzero positive mass. Each packet's mass is nonnegative
by actual cone membership and strict positivity away from zero. The proof of zero
weight implying a zero packet is not replaced by a convention for inverse zero.
The normalized term has a positive-index argument. Every term removed from the
finite sum is proved zero, and the sum of the remaining weights is separately
proved to be one. Thus the reconstruction is a genuine finite convex mixture.

The empty-index case is handled logically rather than excluded by a new premise:
completeness would make every vector zero, which cannot have unit linear mass.
An empty coordinate space is allowed in the classification and has the unique
zero-dimensional behavior. A packet may own no coordinates; the theorem does not
assert every operator is nonzero or every weight is positive on every state.

## The classification is about the actual operators

Entries are defined by evaluating the supplied maps on coordinate basis vectors.
The basis-expansion proof connects those entries to every vector. Positivity is
proved equivalent to nonnegative entries. Completeness forces off-diagonal entries
to vanish because each is nonnegative and their sum is zero. Idempotence forces
diagonal entries to be zero or one. The diagonal sum then determines one owner
per coordinate. The owner is constructed and represents each original map.
Pairwise zero compositions follow from that representation, not an assumption of
orthogonality. The converse theorem verifies that the selectors satisfy all three
input requirements.

## Meaning under a coordinate change

The transport construction uses an actual linear equivalence, its inverse, the
image cone, the pulled-back mass, and conjugated maps. It proves equality of the
weights and transported normalized packets. In the explicit real shear example,
(-1,1) is a valid normalized state in the moved cone with moved mass. It is not
nonnegative in the original coordinates. The separate Haar example remains a
complete idempotent decomposition with orthogonal ranges, but its nonzero detail
has zero ordinary sum and is outside the original positive cone. These examples
separate coordinate signs from admissible-state semantics without conflating them.

## Trust and computation

The four modules use ordinary proof terms, classical choice where stated, and
pinned Mathlib imports. The production syntax scan rejects proof placeholders,
extra axioms, native-decision shortcuts and unsafe/external implementation hooks.
The source-to-result count remains one additional manuscript statement, even
though the implementation has many supporting lemmas and examples. The rational
checker exercises declared finite grids independently of those Lean proof terms,
but remains a same-project implementation, not a universally verified Python tool.
