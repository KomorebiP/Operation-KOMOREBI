# Self-review of the accepted compiler and semantics

## Verdict

**Proved as written**, for the observational fragment and the explicit tagged
interpretation in the accepted source. This is mathematical self-review plus
Lean checking, not an independent referee assessment.

## Dependency chain

Inherited System/run/behavior and ObsFO.Sat
 -> concrete language and tagged structure
 -> correct state-word and observed-term interpretation
 -> correct free/bound environment extension
 -> guarded structural formula translation and satisfaction equivalence
 -> inherited surjective transport / behavioral quotient
 -> standard-syntax preservation and exact fragment truth agreement
 -> locally certified finite test formula
 -> guarded quantifier-free formula and actual Set.Definable endpoint.

The source-prefix normalizer is joined through pathToObsFO and the inherited
normalization proof. It does not replace the primitive operation semantics.

## Obligations reviewed

| Obligation | Outcome |
|---|---|
| Target is actual Mathlib syntax and satisfaction | Passed: no surrogate target predicate in final statement |
| Function interpretation total with explicit wrong-sort branch | Passed; uses disjoint state/value tags |
| Arbitrary finite word order | Passed; pathTerm_realize uses inherited left-to-right run |
| Newest-first source binder versus appended target level | Passed; generic extendVariables_realize |
| Existential reflection does not invent witnesses | Passed; every binder guarded, witnesses eliminated by tag cases |
| Nested binders preserve outer variables | Passed; generic lemma and concrete nested example |
| Formula correctness assumed as certificate field | No; proved by structural recursion/induction |
| Quotient map is actually surjective | Inherited constructed quotient proof used |
| Global defining formula excludes nonstate inputs | Passed; two outer guards and all-tag set equality |
| Parameter-free terminology | Relative to the declared observation language with all value names |
| Null observation/action lists and empty state sort | Universal theorem permits them; finite/Lean boundaries checked |
| Full state equality accidentally preserved | Explicit counterexample rejects it |
| Claim of QE or theory-wide imaginaries | Not made; retained existential is formally not IsQF |
| Python program verified by Lean | Not claimed |
| Upstream theorem/cache trust | Exact pin and source hashes retained; not a cold upstream rebuild |

The target language can express formulas outside the translated fragment. Their
truth need not survive a behavioral quotient. The theorem is not an arbitrary
first-order elementary-map theorem. The tagged graph is an equivalence relation
only on its state sort, not reflexive on the entire disjoint tagged carrier.

## Controls

Positive nested-binder proof accepted. Deliberately false and sorry-placeholder
proofs rejected. Wrong guard, full state-equality transfer, and nonsurjective
witness reflection each fail with a mathematical type mismatch rather than a
missing import. Logs preserve exact diagnostics. Independent finite mutations
also test reversed paths, clobbered binder levels and unguarded witnesses.

## Next unproved implication

Accepted algebraic matrix certificates should produce finite observational test
lists and their local completeness certificates inside the integrated logical
exporter. This connection is not implied merely by the existence of separate
matrix and logical libraries. The present translation/definability block is
complete independently of that subsequent integration obligation.
