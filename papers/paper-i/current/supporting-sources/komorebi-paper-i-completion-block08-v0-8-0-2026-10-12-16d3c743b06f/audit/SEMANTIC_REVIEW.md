# Block 08 semantic and trust-boundary review

This file is a source/type correspondence review, not a kernel interpretation of manuscript prose. The final acceptance receipt and compiled theorem types are authoritative for execution.

## Actual objects

- Scalars for every nonsplit matrix block have typeclass `DivisionRing`, not `Field` or `CommRing`.
- Matrix-module generation is literal left multiplication, with coefficient order checked in row formulas.
- The comparison with the existing canonical seed rank goes through actual submodule spans and generating-family minima.
- The product algebra allows a dependent family of division rings. Product generation supplies independent coefficient matrices only between different algebra factors.
- Inflated natural modules are restricted through the actual coordinate ring homomorphism, not through a hypothetical central `Algebra D A` action.
- The regular-module equivalence takes columns and proves A-linearity. It does not use a false noncommutative transpose multiplication rule.
- Natural-module simplicity is proved, not supplied as a field in a presentation certificate.
- Compatible multiplicity presentations are constructed from actual simple summands. A nonzero projection to a natural column supplies a bijection by Schur's lemma.
- The semilinear change of ring uses the given actual ring equivalence and its inverse. The final ring and module presentations are compatible with one another.
- Radical-top formulas refer to `PaperICompletion7.ModuleTop.RadicalTop`, not a surrogate with assumed dimension or seed number.

## Final public theorem premises

`SemisimpleExistence.exists_semisimple_seed_formula` assumes only a ring, a left module, finite generation and `IsSemisimpleRing`. The theorem's conclusion produces the division rings, positive sizes, multiplicities, ring isomorphism, compatible module isomorphism and rank equality.

`exists_artinian_radicalTop_seed_formula` assumes `IsArtinianRing` instead and constructs the presentations of the literal radical quotient and module top. `exists_finiteAlgebra_seed_formula` derives Artinianity from a field-algebra structure and finite dimension of the ring. The caller still supplies finite generation of the module, as required by the recorded scope.

The formula for any already displayed decomposition is proved separately. Thus internally choosing a presentation does not prevent use of an independently supplied valid presentation.

## Scope conventions retained

The finite positive matrix sizes in Wedderburn decompositions are not optional. The natural-module rank-one corollary is false in size zero; its surrounding natural-simple-module convention is made explicit in Lean. The test suite proves a real zero-size counterexample to the unguarded row criterion.

Finite products of the repeated natural-module copies represent finite direct sums. The outer regular and module decompositions are actual `DirectSum` types. The single-factor multiplicity result additionally has a literal inner `DirectSum` wrapper. The equivalences between these finite models are proved linear equivalences, not a claim that all underlying types are definitionally equal.

The split corollary's original-ring and quotient-ring formulations have different inputs. Both have explicit verified wrappers. Once a split decomposition is supplied, algebraic closure is unnecessary. No claim that every division ring is commutative is introduced.

## Classical dependencies

The actual ring existence theorem is imported from the pinned proved Mathlib Wedderburn-Artin development. The finite simple-summand decomposition and Schur bijectivity are likewise proved dependencies. New source-owned axioms are forbidden by the audit. Standard `propext`, `Classical.choice` and `Quot.sound` remain the allowed transitive foundation axioms.

## Not claimed

No executable decomposition or symbolic canonical-form algorithm, complexity bound or numerical stability guarantee is supplied. No new classical discovery is claimed merely because a theorem is newly formalized here. Individual multiplicity uniqueness beyond what is needed for these actual presentations is not silently advertised as a separate new theorem. Publication PDFs are not rebuilt. The remaining publication records and Papers II–XII are not marked complete.

## Verification strategy

Eight new production files are freshly compiled into a new output directory, including the root aggregator. Forty-six predecessor source/object pairs are authenticated from accepted receipts, rather than freshly recompiled. All logical production declarations and the new boundary module are replayed from an upstream-only kernel environment, with exact owned-name set matching. The seven inherited generated partial runtime helpers remain separately inventoried. They are not reported as separately proof-replayed logical declarations.

The pinned upstream cache is reused. This is Lean's same kernel, not an independently implemented verifier. Failed drafts, foreground interruptions and invalid controls have different recorded statuses and never contribute to a successful proof count.
