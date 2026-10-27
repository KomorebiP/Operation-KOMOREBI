# Literature and API record v0.6.0

## Source question

This bounded block encodes the regular-uncountable initial-cardinal guard, constructs a closed sentence and proves semantic adequacy in concrete ZFSet. It does not make a priority or new-strength claim, and no general novelty search was performed.

Official Mathlib primary documentation checked on 26 September 2026:

* https://leanprover-community.github.io/mathlib4_docs/Mathlib/SetTheory/ZFC/Ordinal.html
* https://leanprover-community.github.io/mathlib4_docs/Mathlib/SetTheory/Cardinal/Regular.html

Broad search queries returned irrelevant results and were not used as evidence. The exact official pages were opened directly. The executable API was then checked in the pinned source aeb72f1e9981b6d35b426b16dca7759be3e7ba06, especially ZFC.Ordinal, Cardinal.Regular, Cardinal.Cofinality.Basic, Cardinal.Cofinality.Ordinal, and ModelTheory.Semantics. No assumption of identity between changing web documentation and pinned source is needed.

The ordinal API proves equivalence between von Neumann ordinals and the ambient ordinal representation. It also characterizes ordinals as transitive sets of transitive sets. The regular-cardinal API defines regularity as infinitude plus kappa <= cof(kappa), and supplies the small-index supremum bound. The converse boundedness characterization and all set/formula translations are proved in the project.

Classification: checked representation and semantic translation of the independently classified known global principle. No new set-theoretic consistency strength, first-formalization claim or arbitrary-model absoluteness is asserted. The historical strong-compactness terminology check is retained below, not silently promoted to a fresh broader literature result.

## Historical v0.5.0 and earlier records

# Literature and interpretation record v0.5.0

## Current source question and scope

This block asks how the pinned Mathlib ZFSet and model-theory APIs represent sets, cardinality, intersections and first-order syntax. It does not make a novelty or first-formalization claim, and it does not repeat a global large-cardinal literature search.

Official Mathlib documentation checked on 26 September 2026:

* https://leanprover-community.github.io/mathlib4_docs/Mathlib/SetTheory/ZFC/Basic.html
* https://leanprover-community.github.io/mathlib4_docs/Mathlib/SetTheory/ZFC/Cardinal.html

These documents are primary library documentation, but the executable authority for this release is the pinned source revision aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The compiled imports also use ZFC.Ordinal and ModelTheory.Semantics from that revision. The dependency source and binary cache are not bundled here.

The relevant distinctions were checked in source and used explicitly:

* ZFSet is a concrete set universe constructed in Lean's ambient metatheory. A theorem about this structure is not an object-language ZFC derivation.
* Cardinality uses the small carrier of a ZFSet. The new round-trip and family-equivalence proofs connect that carrier to the predecessor's universe-polymorphic types.
* Unbounded ZFSet.sInter sends the empty family to the empty set. The filter operation in this release is instead relative to its carrier.
* ZFSet.Definable is not used as a substitute for first-order formula syntax. This release constructs actual FirstOrder.Language.Formula terms in an independently specified membership-only language and proves their realization theorems.

The new equivalences are proved within the source, rather than imported as external literature assertions. Classification: checked implementation and semantic translation of a known principle. No new consistency strength is claimed. The regular-uncountable guard and arbitrary-model/object-language proof remain outside the current interpretation theorem.

## Retained predecessor literature check

The following is the historical v0.4.0 source record. It was not silently upgraded into a fresh check of a different version or a broader theorem in this block.

# Literature and terminology check v0.4.0

## Source question

Does the independently defined all-set CompleteFilterExtension/FineUltrafilterPrinciple correspond to the standard strong-compactness formulation at regular uncountable kappa? This is a terminology and overlap check, not a global novelty search and not a formal proof imported from literature.

## Authenticated primary source

Yair Hayut, *Partial strong compactness and squares*, arXiv:1804.05758v2, version dated 16 September 2018.

HTML: https://arxiv.org/html/1804.05758v2

PDF: https://arxiv.org/pdf/1804.05758v2

Checked on 26 September 2026. The HTML version metadata and PDF pages 1 and 5 were inspected. No licensed or private source was uploaded. Source content is not bundled or used as executable proof input.

## Exact extraction and translation

Definition 1 assumes a regular kappa. Its lambda-filter extension property extends every kappa-complete proper filter on lambda to a kappa-complete ultrafilter. Its lambda-strong compactness property requires a fine kappa-complete ultrafilter on P_kappa(lambda). The introduction distinguishes global equivalent formulations from local versions, which need not be equivalent at the same lambda.

Our CompleteFilterExtension quantifies over all sets X in the selected universe, not one fixed lambda. Our FineUltrafilterPrinciple quantifies over all sets I and uses the actual P_kappa(I). Thus their all-sets, uncountable regular interpretation is the familiar global strong-compactness formulation. The Lean development proves its own implication cycle with these independent definitions.

Theorem 3 treats a more refined local lambda-level equivalence with L_(kappa,kappa) compactness and assumes lambda^(<kappa)=lambda. That theorem is not claimed as formalized here. The reverse direction uses Boolean membership/complement/small-intersection requirements, an overlap with our semantic constraint construction. The literal introductory sentence of that reverse proof calls the starting F an ultrafilter, while the theorem and surrounding argument concern extending a filter. The project follows the independent proper-filter definition and does not assume ultrafilter maximality in its starting object.

Classification of overlap: known after translation for the global filter/ultrafilter characterization; a direct checked implementation in the project's residual interface. No claim of mathematical priority, first formalization, or new consistency strength. No comprehensive novelty or forward-citation search was undertaken because this block makes none of those claims.

## Formal API

The current official Mathlib CardinalInterFilter documentation was checked:

https://leanprover-community.github.io/mathlib4_docs/Mathlib/Order/Filter/CardinalInter.html

Actual compilation uses the pinned Mathlib source at aeb72f1e9981b6d35b426b16dca7759be3e7ba06, not an assumed identity between today's documentation and that revision. The relevant interface means closure under intersections of fewer than kappa large sets, with strict cardinal inequality.

## Retained older interpretation

The predecessor recorded the Stacks Project product-difference-complex description of countable derived inverse limits, tag 07KV. That comparison was not re-proved or formalized in this block. The explicit integer cokernel and restriction maps remain checked, while their identification with Mathlib derived functors remains open.
