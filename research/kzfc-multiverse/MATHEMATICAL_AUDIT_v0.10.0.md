# Mathematical audit of the internal arithmetic block

## Claim versus executable check

Claim: every model of the unchanged encoded ZFC theory satisfies the original guarded small-product arithmetic sentence and consequently the original guarded Extension -> Compactness sentence.

Executable check: rebuild all 48 project mathematical modules against the pinned Mathlib cache, re-elaborate each with warnings as errors, and audit all 502 named theorem dependencies. The universal assertion is justified by the checked theorem terms, not by a finite sample of models.

## Noncircular dependency checks

1. Ordinal comparison uses explicit first-order definable bounded induction and internally represented transitive bounds. It does not use SmallProductClosed or external WellFounded.
2. The bounded-ranking constructor assumes smallness only of strict predecessor sets. It does not assume totality, a ranking graph, product smallness or small-union closure.
3. Partial rankings are elements of the internal powerset of W times K. Their compatibility is proved using an internal disagreement set. Totality is then proved, not stored as a field.
4. Least-rank existence restricts the partial graph to its small predecessor domain. Its image is internally small and the guard supplies a bound. The offset is combined by ordinal comparison, not cardinal arithmetic.
5. Small binary unions use shifted ordinal copies from the ranking constructor. This occurs before and independently of general union or product closure.
6. Rowwise boundedness assumes factor smallness but not product smallness. The internally represented row-bound selector has small image because its domain is small, independently of the rectangle.
7. The induction hypothesis for a times b concerns only smaller first-coordinate ordinals i in a. The other predecessor component is a slice which embeds into j.
8. The final small-product graph is explicitly induced by the two factor injections and then transported into a small ordinal rectangle.
9. The original Guard, AxiomSemantics, constraint class, productArithmeticSentence, Theta and theory definitions were not modified.

## Boundary checks

* The generic induction theorem is restricted to a supplied first-order formula. It is not an induction principle for arbitrary external predicates in ill-founded models.
* WellOrderOn requires least points only for subsets which are elements of the model.
* Every family on which internal boundedness is applied is formed using actual Separation or Replacement and is proved internally small.
* An assumed KZFC model yields a witness inside that model. No KZFC model or uncountable cardinal is constructed.
* The guarded proof need not establish a general cardinal-square theorem at arbitrary internal cardinals. Its exact target is the original regular-guarded product closure.

## External baseline

The ordinary cardinal-arithmetic conclusion is known, not a novelty claim. Mathlib's official Cardinal.Arithmetic documentation states Cardinal.mul_lt_of_lt and the infinite-cardinal multiplication identities. This project does not apply that ambient theorem as a substitute for an internal graph witness in an arbitrary model.

The primary documentation was inspected on 2026-09-26:
https://leanprover-community.github.io/mathlib4_docs/Mathlib/SetTheory/Cardinal/Arithmetic.html

This external reference authenticates the ordinary arithmetic baseline. It is not a proof of the project's model-specific implementation, which is checked by Lean.

## Residual trust

This audit was performed by the same development agent. It is not a claim of an independent human or second-model review. The Lean kernel/compiler, pinned dependencies, ambient logical axioms and platform remain trusted. Hashes certify provenance and distribution integrity, not independent logical soundness.
