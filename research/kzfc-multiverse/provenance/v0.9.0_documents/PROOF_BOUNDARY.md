# Proof boundary v0.9.0

## Completed for arbitrary models of encoded ZFC

The predecessor's 33 mathematical modules and 378 named declarations are unchanged. Seven new modules add 61 named declarations, for 439 total.

1. Smallness passes to internally represented subsets. Empty, singleton and pair supports are small under the existing inductive-member hypothesis. The original guard already bounds unions of small families that are themselves subsets of K.
2. The cone filter on the internally small subsets of I exists as an internal set. It is proper, fine and complete under an explicit SmallUnionClosed(K) premise. Its completeness proof uses internally selected supports, an internally small Replacement image family and an internal union.
3. Internal complete-filter extension plus SmallUnionClosed and the existing inductive-member condition produces the internal fine-ultrafilter principle. This combines with the preserved fine-to-compactness theorem.
4. Conversely, the internal fine-ultrafilter principle implies SmallUnionClosed without assuming the guard. Completeness is applied only to internally existing small families of large cones.
5. Under the original Guard(K), SmallUnionClosed(K) iff SmallProductClosed(K). The nontrivial direction constructs a common ordinal bound for all small members and an internal injection of their union into the product of the indexing family and that bound.
6. Hence, under Guard(K) and Extension(K), Fine(K) iff SmallProductClosed(K). A closed membership-language sentence expressing this reduction is a proved semantic consequence in every model of the encoded ZFC theory.
7. With an explicit modelhood premise for productArithmeticSentence, the original guarded extension-to-compactness sentence follows in arbitrary models. The arithmetic premise is visible in the Lean theorem type.

## Completed for concrete ZFSet only

SmallProductClosed at every infinite initial-cardinal code is proved using exact translations and Mathlib cardinal arithmetic. Consequently Guard implies SmallUnionClosed, and Guard plus Extension implies the internal fine principle and internal constraint compactness in ZFSet. The corresponding concrete closed-sentence theorems are checked.

No ZFSet model of KZFC is constructed. The theorem extracting an internal compactness witness from such modelhood assumes that modelhood as a premise.

## Exact remaining obligation for the first arrow

    model_zfc_productArithmeticSentence:
      M models zfcTheory -> M models productArithmeticSentence

Here productArithmeticSentence is literally the first-order assertion that products of internally small sets are internally small at guarded parameters. This is ordinary cardinal arithmetic, not a proposed new axiom. The project has not yet derived its arbitrary-model version from its explicit ZFC schemas. The sentence has NOT been inserted into zfcTheory or kzfcTheory and AxiomSemantics is unchanged.

An external Mathlib theorem about Cardinal cannot be substituted for this internal proof. External and internal cardinality, available function graphs, powersets and well-foundedness are not identified.

## Other remaining obligations and nonclaims

* The internal constraint-compactness-to-complete-filter-extension converse remains unfinished.
* Therefore the full arbitrary-model equivalence with the original Theta remains unfinished.
* No extraction into a separately specified first-order proof calculus.
* No uncountable existence, truth of Theta, KZFC model, independence, relative consistency, new strength or first-formalization claim.
* No arbitrary higher-derived residual classification or Mathlib derived-functor identification of the integer cokernel.

## Trust and evidence

The final verdict must be read from RESULTS.json and the completed staged-session record. The named-theorem count includes auxiliary lemmas and interpretation identities. The dependency cache is reused, while project build products are rebuilt. Standard Lean axioms, compiler/kernel, pinned dependencies and platform remain trusted. Hashes establish provenance, not an independent proof of Lean soundness. Historical incomplete attempts are retained separately and cannot serve as active PASS evidence.
