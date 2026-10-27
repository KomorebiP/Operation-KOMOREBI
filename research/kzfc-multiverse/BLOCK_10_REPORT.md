# Block 10: internal product arithmetic and the forward implication

## Result

The v0.9 arbitrary-model arithmetic premise is discharged:

    M models zfcTheory -> M models productArithmeticSentence.

It follows, with the unchanged original guard:

    Extension -> Fine -> Compactness -> Reflection.

The actual `guardedExtensionCompactnessSentence` is now a semantic consequence of the explicit ZFC theory. The theorem extracting a compactness witness from an assumed KZFC model no longer requires an extra arithmetic premise.

## New files

1. InternalOrdinalOrder.lean: definable bounded induction, ordinal comparison and internal membership well-orders.
2. InternalOrderGraphs.lean: internal graph retyping, images, append operations, and internal well-order interface.
3. InternalRankingConditions.lean: actual syntax and semantics of partial rankings; existence and uniqueness of least bounds; compatibility.
4. InternalBoundedRanking.lean: union of compatible partial graphs, extension at a least missing point, total injective ranking.
5. InternalFiniteUnions.lean: shifted ordinal copies and small binary unions.
6. InternalLexicographicOrder.lean: internal lexicographic rectangle relation, least points, and predecessor decomposition.
7. InternalRectangleBounds.lean: internal row graphs, row-bound selector and two-stage range bound.
8. InternalProductArithmetic.lean: definable induction on rectangles, factorwise product injections, and discharge of the original all-model sentences.

The source inventory adds 63 declarations, including auxiliary and syntax interpretation lemmas. All 40 predecessor mathematical modules and all 439 prior theorem statements are unchanged.

## Why this is not a hidden assumption

The arithmetic predicate is not inserted into ZFC, AxiomSemantics, Guard, or constraint admissibility. Internal well-ordering is required only for internally represented subsets. Every application of induction has an actual first-order formula. Every graph needed as a witness is supplied by internal set-existence arguments.

The bounded-ranking theorem is not a definition containing totality. Its partial graph structure has no totality field. Totality is proved by the union and least-missing-point argument.

The rectangle range-bound lemma assumes only factor smallness, not product smallness. Thus its use to shrink the full ranking image is noncircular.

## What remains

The internal constraint-compactness-to-filter-extension converse remains. Until it is proved, do not claim the full arbitrary-model equivalence. No model existence or truth of the new axiom follows from these conditional and consequence theorems.

## Evidence

Read the active verification/RESULTS.json and process_record.json. Individual development builds precede the independent clean staged audit and are not substitutes for it. Failed parser/elaboration attempts and interrupted audit launches are retained. The final release summary records the completed audit and archive result.

## Completed verification

Session `74eb35d0-292b-4dc1-96d5-c9cef7eb4826` finished with PASS and staged-completion exit 0.
All 103 compiler commands matched their expected outcomes, all 502 theorem declarations
were covered, and all 40 predecessor mathematical modules matched byte-for-byte.
The full root build reported 1,249 jobs including dependencies. The only observed
axiomatic dependencies were Classical.choice, Quot.sound and propext.
