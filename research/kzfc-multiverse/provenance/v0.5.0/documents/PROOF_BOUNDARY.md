# Proof boundary v0.5.0

## Kernel-checked in this release

* All 12 predecessor mathematical modules and their 97 declarations, unchanged.
* Exact round trips for set subsets and bounded families, preservation of cardinality, relative intersections, filters, ultrafilters and extension.
* Representation of every Type u by the small carrier of a ZFSet.{u}, with exact transport back to the all-types proposition.
* Equivalence of set-coded injections with carrier embeddings, and exact interpretation of strict smallness at initial-ordinal cardinal codes.
* A membership-only Mathlib first-order formula Phi(K), with one free parameter.
* The equivalence of its concrete ZFSet interpretation with CompleteFilterExtension at every cardinal, and with the specified residual principle at regular cardinals.
* Aleph0 truth and failure at every infinite successor, transferred through the actual syntax interpretation.
* A regression refuting positive-cardinal completeness based on unbounded empty-family ZFSet intersection.

## Not proved or assumed

* No regular uncountable cardinal with the compactness/extension property is proved to exist or inserted as a custom axiom.
* No closed first-order sentence encoding the regular-uncountable existence guard is supplied. Phi alone is a parameter formula. Its unguarded existential closure is not the intended large-cardinal assertion.
* No first-order derivation of the comparison from the ZFC axiom set, nor an interpretation theorem over every arbitrary model of ZFC.
* No internal/external absoluteness of cardinality or completeness in arbitrary models.
* No independence, relative consistency, or new consistency-strength result.
* No classification of arbitrary higher-derived residual systems and no comparison of the explicit integer cokernel with Mathlib right-derived functors.
* No general failure of all translations between residual degrees. Earlier fixed-system non-flattening must not be confused with a translation-invariant impossibility.

## Metatheory and audit scope

Lean 4.34.0-rc2 checks the project using the pinned Mathlib revision. The theorem audit reports only Classical.choice, Quot.sound and propext. These are ambient Lean dependencies, not a list of ZFC axioms from which an object-language derivation was extracted.

The audit covers all 173 named theorem declarations in the project's explicit source format. Auxiliary and interpretation lemmas are included in that count. Source scans exclude custom axioms, proof placeholders, unsafe declarations, native_decide, implemented_by and run_tac in active source. The negative controls are deliberately invalid temporary test files and are not imported by any theorem.

The clean run removes the project's build products, not the preverified dependency cache. The proof checker, compiler binaries, cached dependencies and surrounding platform remain in the trust boundary. Checksums and manifest validation establish provenance and record integrity, not a second independent proof of Lean's soundness.

## Exact status

Semantic membership-language interpretation: COMPLETE for the stated formula and concrete ZFSet structure.

Internal ZFC derivation and closed guarded existence axiom: OPEN.

Uncountable existence, independence and relative consistency: NOT CLAIMED.
