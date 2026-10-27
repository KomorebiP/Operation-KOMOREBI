# Continue from v0.6.0

Use this archive as the authoritative source. Read THEORY.md, PROOF_BOUNDARY.md, the three new modules and the active verification record before modifying it.

## Completed

Do not redo the guard or closed sentence. `guardedSentence_iff_residualExistence` and `guardedSentence_iff_filterExtensionExistence` classify the actual membership-only closed sentence Theta in concrete ZFSet. `guard_iff_exists_cardinal` treats every possible set witness. The unguarded sentence is proved true, and aleph0 is proved not to witness the guarded one.

`GuardedTheory.lean` adjoins Theta to any explicitly supplied base theory T and proves the model insertion rule. It does not supply T = ZFC.

## Next substantive obligation

Define an explicit first-order ZFC axiom theory in the same membership language, with precisely coded schemas. Then either construct an internal derivation for the target comparison or prove an appropriately internalized comparison for arbitrary models. Do not silently use external powersets, functions, cofinalities or cardinalities in place of the model's own objects.

A bounded first step is a representation-independent semantics layer for the guard's set quantifiers and function graphs, with the exact axioms used by each ordinal and cardinal lemma recorded. It must not package the desired classification into an assumed model interface.

## Reproduce

Use the pinned Lean kit and follow REPRODUCE.md: `verify_staged.py start`, repeated `next --count 5`, then `finish`. Do not restart between batches. Then regenerate and validate the manifest. Read each actual compiler exit and the final staged-completion status. Historical partial monolithic attempts do not establish success.

No uncountable existence assumption should be added merely to make an interpretation theorem compile.
