# Komorebi KZFC Residual Reflection v0.9.0

This checkpoint proves the internal cone-filter construction and an exact support-arithmetic reduction in arbitrary models of the project's explicit first-order ZFC theory. It does not yet finish the original arbitrary-model filter-extension-to-compactness implication.

For a model M and a parameter K satisfying the unchanged regular uncountable initial-cardinal guard, the new theorems give

    Extension_M(K) -> (Fine_M(K) iff SmallUnionClosed_M(K) iff SmallProductClosed_M(K)).

SmallUnionClosed and SmallProductClosed are separately stated closure predicates on actual internal sets. They are not new fields of AxiomSemantics, not axioms of ZFC/KZFC, and not definitions of Fine. The existing fine-to-compactness theorem therefore yields compactness and reflection when the explicit small-product premise is available.

The small-product premise is fully discharged in concrete ZFSet. Consequently the original guarded extension-to-internal-compactness implication is proved there. The corresponding ordinary cardinal-arithmetic theorem has not yet been formalized from encoded ZFC in arbitrary models. This distinction is the principal proof boundary.

## Contents

Seven new mathematical modules add 61 named theorem declarations. All 33 immediate predecessor mathematical modules and their 378 declarations are preserved byte-for-byte. The resulting named theorem inventory has 439 entries, including supporting lemmas and interpretation identities.

* `InternalSmallSupports.lean`: internal subsets, finite supports and bounded ordinal families.
* `InternalConeFilter.lean`: actual internal cones, proper filter, completeness, fineness and conditional extension application.
* `InternalFineSupportClosure.lean`: fine complete ultrafilters force small-union closure.
* `InternalUnionReduction.lean`: uniform bounds and an internal injection of a union into a family product.
* `InternalSupportEquivalence.lean`: small-union/product equivalence and exact fine-principle reduction.
* `ZFSetSupportClosure.lean`: concrete arithmetic discharge and complete concrete forward implication.
* `InternalConeFormula.lean`: closed membership-language reduction and conditional consequence sentences.

Read `BLOCK_09_REPORT.md`, `PROOF_BOUNDARY.md` and `CONTINUE_HERE.md` before extending the project. Reproduction commands are in `REPRODUCE.md`. The actual verification verdict is `verification/RESULTS.json`, not this prose. The source archive excludes the compiler and dependency caches.

No new consistency strength, uncountable cardinal existence, KZFC model, independence, relative consistency or priority claim is made.
