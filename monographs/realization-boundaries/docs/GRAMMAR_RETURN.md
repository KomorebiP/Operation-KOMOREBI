# Grammar escape closure

Base checkpoint: Realization Boundaries Lean v0.6.0 checked archive.
Base archive SHA-256: `032f61f0e176f0f3abfeb3615b8936ebd9edb7c3f9a07b6b8ad25877ec7aef70`.
Owned production source: `RealizationBoundaries/GrammarEscape.lean`.
Final source SHA-256: `2340db91c8fb37e3deb142e60f580f3a787c5e44dfce9f68d48295554c05f38e`.

## Exact results

The source closes the printed contracts 10.1 and 10.2. It does not impose an effective evaluator, decidable validity or computable selection of semantic representatives.

* `repeatedDiagonal` is the exact even/odd paired-index selector from equations (10.1) and (10.2). The even and odd coordinate formulas are proved.
* `repeatedDiagonal_infinite_disagreement` opposes each table representative on an injective infinite coordinate block.
* `repeatedDiagonal_free_infinite_disagreement` preserves each distinct pair of free binary inputs on an injective infinite odd block.
* `grammarEscape_not_output` excludes isomorphism with **every** output of an arbitrary natural-number indexed group-valued semantic table, including outputs not belonging to the paired family.
* `grammarEscape_pairwise_nonisomorphic` and `grammarEscape_no_embedding` establish the full isomorphism and embedding separation for distinct free selectors. Applying the latter with the inputs swapped gives the other direction.
* `grammarEscape_family_cardinality` gives the exact continuum cardinality of the actual escaped ambient-subgroup family. In conjunction with pairwise nonisomorphism, this gives continuum many isomorphism types, not merely continuum many presentations of fewer groups.
* `grammarEscape_completion`, `grammarEscape_countably_infinite`, `grammarEscape_residuallyFinite`, and `grammarEscape_reduced` supply the printed structural conclusions. Reducedness excludes embeddings from every nontrivial divisible additive group, rather than just rational summands.
* The `countableGrammarEscape_*` interface handles **any countable code type** directly, including a valid finite-string subtype. `countableDescriptionIndex` explicitly chooses an injection into naturals; `reindexedSemanticRepresentative_at` proves that extension through that injection retains each actual semantic representative. No surjective enumeration of an empty code type is assumed.
* `DescriptionGrammar` packages validity/semantics in the `denotes` relation and a natural-number length. `shortestLength` is a genuine minimum over valid descriptions, with an actual shortest witness and the minimality property.
* `DescriptionGrammar.admissible_expansion` proves semantic realizability monotonicity.
* `DescriptionGrammar.admissible_expansion_length` and `admissible_expansion_complexity` prove the exact shortest-description length bound. The length-overhead hypothesis is required only for valid source descriptions. No monotonicity of the overhead function is assumed or needed.
* `DescriptionGrammar.complexity` takes values in `WithTop Nat`; `grammarEscape_complexity_infinite` proves infinite complexity in the specified fixed semantic grammar.

The finite syntax countability lemma supplied by `Reachability.lean` can be instantiated independently; this file does not add an import dependency on that parallel work.

## Verification

Final clean compiler receipt: `verification/development/GrammarEscape_007.json` (exit 0, warnings as errors, autoImplicit false, 2.56 seconds).
Final module kernel replay: `verification/development/GrammarEscape_kernel_replay_007.log`.
Explicit axiom checks: `verification/development/GrammarEscape_axioms_final.log`; main escape, continuum, embedding, reducedness, generic countable-code and complexity/translation theorems use only `propext`, `Classical.choice`, `Quot.sound`.
Production contains 27 public named theorem declarations plus one private proof helper.

Earlier compiler failures are implementation diagnostics, retained in development evidence: unused/deprecated simplifier names, lambda reduction needed before arithmetic, local classical decidability, and a nested dependent-if rewrite. They exposed no failed mathematical implication. No failed receipt is treated as accepted evidence.

## Integration instructions

Add `GrammarEscape` after `ClassificationConsequences` to the module manifest and add the root import. Run the coordinator's full clean source audit, contracts, rejections and kernel replays before promoting the registry. Do not identify module-local compilation with the full accepted release receipt.

Useful positive contracts are the exact types of `grammarEscape_not_output`, `grammarEscape_family_cardinality`, `countableGrammarEscape_not_output`, `grammarEscape_reduced`, `grammarEscape_complexity_infinite` and `DescriptionGrammar.admissible_expansion_length`.

Useful rejection controls are a claimed isomorphism with one semantic output (contradicted by `grammarEscape_not_output`), a claimed embedding between two distinct free selectors (contradicted by `grammarEscape_no_embedding`), and a false finite complexity conclusion (contradicted by `grammarEscape_complexity_infinite`). The existing finite-toggle equality theorem already guards the failure mechanism of an ordinary one-disagreement diagonal.
