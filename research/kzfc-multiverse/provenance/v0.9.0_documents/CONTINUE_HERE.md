# Continue from v0.9.0

Use this release as the source checkpoint. Preserve all 40 mathematical modules and the verified theorem statements. Do not weaken Guard or add closure fields to AxiomSemantics.

## Immediate target

Prove, from the existing encoded ZFC axioms in arbitrary M,

    M models zfcTheory -> M models InternalConeFormula.productArithmeticSentence.

Equivalently derive SmallProductClosed(K) from Guard(K). This is an ordinary internal cardinal-arithmetic theorem, not a new assumed axiom. The corresponding concrete ZFSet theorem is already proved and is not a replacement for the arbitrary-model result.

Once this target is checked, model_zfc_extensionCompactness_of_arithmetic immediately closes the original internal Extension -> Compactness implication. fine_iff_productClosed_of_extension also closes Extension -> Fine.

## Available completed pieces

* InternalSmallSupports: subsets, finite supports and ordinal-family union bound.
* InternalConeFilter: actual internal cone-filter construction and complete extension application given SmallUnionClosed.
* InternalFineSupportClosure: Fine -> SmallUnionClosed without a guard.
* InternalUnionReduction: uniform ordinal bound, internally selected injection family and union embedding into a product.
* InternalSupportEquivalence: SmallUnionClosed iff SmallProductClosed under Guard.
* ZFSetSupportClosure: full arithmetic discharge in concrete ZFSet.
* InternalConeFormula: actual closed reduction sentences and conditional original forward implication.

## Arithmetic proof route

See INTERNAL_PRODUCT_PROOF_PLAN.md. It outlines the standard infinite-cardinal-square argument but is NOT an already compiled internal proof. The missing infrastructure concerns internally coded well-orders, ordinal order types, cardinal representatives and the corresponding induction argument. Do not infer that an arbitrary model is externally well-founded.

## Second outstanding arrow

Internal ConstraintCompactness -> internal complete-filter Extension. Encode Boolean filter requirements, relation table, scope graph, satisfying truth assignment and resulting ultrafilter using actual internal sets. The external v0.4 proof is a blueprint, not an internal proof.

No uncountable existence, KZFC model, independence or new consistency strength is claimed.

## Reproduction

Follow REPRODUCE.md and preserve pin versions. The staged verifier records every actual compiler exit and can resume in short synchronous batches. Never treat an incomplete earlier build as a final PASS. Preserve failed attempts, regenerate the theorem audit for every new theorem, and run archive validation after final verification.
