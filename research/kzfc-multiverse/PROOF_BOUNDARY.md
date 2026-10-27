# Proof boundary v0.11.0

The multiverse-residual additions are documented in `PROOF_BOUNDARY_v0.11.0.md`.
The v0.10.0 depth-zero KZFC boundary is retained below unchanged for ancestry.

---
# Proof boundary v0.10.0

## New proved content

The original guarded small-product arithmetic statement is proved for arbitrary membership structures satisfying the unchanged encoded ZFC axioms, not only for concrete ZFSet.

The proof constructs:
* Definable bounded induction from actual Separation and Foundation instances.
* Internal ordinal comparison and membership well-orders.
* A bounded internal ranking of any internally well-ordered set whose strict predecessor sets are internally small.
* Shifted ordinal embeddings and internally small binary unions.
* An internal lexicographic order on ordinal rectangles.
* Bounds on rectangle-map images using successive internally selected row bounds.
* Ordinal-rectangle smallness by definable induction.
* Actual internal product injections induced by factor injections.

The original closed `productArithmeticSentence` and `guardedExtensionCompactnessSentence` are now semantic consequences of encoded ZFC in every membership structure. An assumed model of KZFC has an internal guarded constraint-compactness witness.

No additional arithmetic premise is needed in these new conclusions. The old conditional consumer theorems remain unchanged.

## Preservation

All 40 predecessor mathematical modules, including AxiomSemantics, Guard, zfcTheory, kzfcTheory, Theta, Small and constraint admissibility, are unchanged. New modules prove their hypotheses rather than adding fields or weakening definitions.

All 439 predecessor theorem declarations are retained. Eight modules add 63 declarations, giving 502 named declarations. Counts include auxiliary, internal-construction and interpretation lemmas.

## Still not proved

* The internal ConstraintCompactness -> Extension converse.
* The resulting full arbitrary-model residual-constraint/filter-extension equivalence.
* A separately exported derivation in a specified first-order proof calculus. Current all-model results are Lean-checked semantic consequences.
* Uncountable compactness-cardinal existence, truth of Theta, or existence of a model of KZFC.
* Independence, relative consistency, new consistency strength or first-formalization claims.
* Classification of arbitrary higher-derived systems or comparison of the explicit integer cokernel with Mathlib right-derived functors.

## Internal versus external scope

Induction is proved for explicitly supplied first-order formulas on an internal transitive bound. No induction principle for all external predicates on a possibly externally ill-founded model is asserted.

The internal well-order predicate requires least points only for subsets represented inside the model. Its use never assumes an external WellFounded relation.

The partial-ranking family, its union, missing-domain set, predecessor image, row graphs and selectors are all supplied by internally applicable set axioms. An externally chosen mathematical object is not treated as an internal function graph.

## Trust

The active clean verification must cover the complete command plan, all named theorem axiom outputs, unchanged source hashes, predecessor equality and negative controls. Compiler/kernel binaries, Lean's ambient axioms, pinned dependency source/cache and the platform remain trusted. The project build cache is cleared; the dependency cache is reused.

Checksums establish record and distribution integrity, not an independent proof of Lean soundness. Historical incomplete attempts are retained but are not active PASS evidence.
