# Proof boundary v0.7.0

## Newly proved

* An explicit membership-language ZFC theory with eight fixed sentences and all finitely parameterized Separation and exact Replacement instances.
* Exact axiom semantics for every arbitrary membership structure. The schema semantics are indexed by syntactic formulas, not arbitrary external predicates.
* ZFSet satisfies the entire explicit theory, including both full schemas and internally represented choice graphs.
* The guarded sentence has an exact internal interpretation in every membership structure. All size, product, graph, subset-family and filter witnesses are internal elements.
* The actual extension is ZFC plus the already constructed Theta. Its arbitrary-structure model condition is exactly the axiom semantics together with the internally read guarded extension.
* In ZFSet, modelhood of this explicit extension is equivalent to the previously classified residual/filter existence assertions, with the base-model premise now proved.
* Internal no-self-membership and no-two-cycle consequences of Pairing and Foundation, and the no-universal-set consequence of a single actual Separation instance.

## Not proved or assumed

* No uncountable compactness cardinal, truth of Theta, or model of KZFC is asserted to exist.
* No custom Lean axiom is introduced.
* No full internally coded residual-constraint/complete-filter classification for every arbitrary ZFC model, and no extraction of an object-language proof of that classification from ZFC, is supplied.
* No equality or absoluteness of a model's internal and external powersets, cardinalities, graphs, ordinals, or completeness notions is assumed.
* No external well-foundedness of arbitrary ZFC models is asserted.
* No independence, relative consistency, new large-cardinal strength or first-formalization claim is made.

## Interpretation versus internal mathematical classification

The arbitrary-structure theorems decode actual syntax into its internal quantified meanings. They are not a proof that the model's internal compactness cardinal is strongly compact externally. The deeper residual-constraint comparison is a distinct unfinished obligation.

The ZFSet model theorem is proved in Lean's ambient type theory. It is not a proof by ZFC of its own consistency.

## Preservation and trust

All 20 predecessor mathematical modules and their 210 named theorem declarations are preserved byte-for-byte. Six new modules add 80 declarations, including interface and supporting lemmas, for 290 total.

The fresh verification rebuilds project artifacts, not the pinned dependency cache. Runtime binaries, compiler/kernel, pinned Mathlib dependencies, ambient logical axioms and the platform remain trusted. The source scan, full named-theorem axiom audit, negative controls, before/after input hashes, compiler exits and final staged-session verdict must all pass before completion is claimed. Checksum and manifest checks verify provenance, not Lean's soundness independently.
