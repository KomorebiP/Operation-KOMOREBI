# Failure ledger — v0.26

The retained `development/ATTEMPTS.jsonl` and `development/logs/` are development records, not a claim that failed drafts were checked. Final evidence is the clean direct replay in `RESULT.json`.

## Environment

An attempted streaming container invocation returned `StreamingExecNotEnabledContainerError`; no work was counted from that launch. All subsequent commands were synchronous and bounded. The seven-part portable runtime assembled to its prescribed SHA-256 and extracted successfully. The final direct replay uses the existing pinned Mathlib compiled cache.

## Rejected drafts, then repairs

- A field named `section` conflicted with Lean syntax; it was renamed `lift`.
- A guessed `Mathlib.RepresentationTheory.Rep` import did not exist; the precise `Rep.Basic` import was used.
- Kernel submodule membership did not simplify to a ring-map equality automatically; the equality was introduced explicitly.
- An extra subtype-extensionality step followed an `ext` tactic which had already descended to underlying values; the redundant step was removed.
- The change-of-section proof needed a right-associated square-zero product before noncommutative normalization could close the goal.
- A proof variable shadowed a group element; the proof variable was renamed.
- A deprecated conditional rewrite produced a warning under warnings-as-errors; the accepted proof uses current simplification syntax.
- Relative cochain differential arguments required explicit underlying functions, and the low-degree cocycle lemma had an implicit representation argument.
- Semireducible representation coercions prevented a generic `map_add` rewrite; the action formula was made explicit.
- The correct matrix ring-homomorphism API is `q.mapMatrix`, not the guessed `Matrix.mapRingHom`.
- Finite subgroup membership was unfolded to its finite disjunction for kernel-checked `decide`.

Scratch `Probe.lean` and `ExampleProbe.lean` contained API checks with intentionally unknown names during discovery. They are excluded from release production source and not counted as proofs. Their logs, where recorded, remain in the development ledger.

## Mathematical negative controls

The no-lift examples are intentional completed proofs, not implementation failures. They refute the shortcuts `every compatible defect is correctable` and `absolute vanishing implies prescribed-subgroup liftability`. They do not refute Strong Artin.

## Verification scope

The fresh release replay has one unchanged historical source dependency, nine new modules, and one axiom audit. It is not a replay of every ancestral declaration. No statement that an arbitrary H² class vanishes is counted as proved.
