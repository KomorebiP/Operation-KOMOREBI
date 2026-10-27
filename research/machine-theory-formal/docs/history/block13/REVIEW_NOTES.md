# Block 13 review and execution notes

The exact target is Core 7.4, Reviewed Core 0.2, `r:lineage`. The general mathematical argument and new code were reviewed against the source. The source book was not edited. The external theorem dependencies are actual imported Mathlib conditional-expectation, measure and nonnegative infinite-sum results. Their use and instantiated assumptions are visible in the proof terms.

## Corrections and actual failures

The exact runtime was recovered by reusing an existing installation whose compiler, nine dependency revisions and selected binaries matched the preserved inventory. Direct executable discovery failed on this host without the supplied adapter. The conditional-expectation smoke then exceeded the inherited 3,072 MiB Lean internal limit. Its first replay also failed because no object had been produced. Compilation and replay passed after setting 4,096 MiB and using the preserved executable-location adapter. `evidence/runtime13` retains the failure and successful retry. This is an environment change, not a change to the compiler, source theorem, or allowed axioms.

Main-proof authoring errors involved implicit ambient measurable-space selection, unused section variables, a stopping index inferred as an extended natural instead of a natural, and a divergent-union simplification. They were corrected with explicit types and local proofs. The final API directly restates the source using Mathlib conditional expectation rather than only repeating a project abbreviation.

Finite-example authoring builds failed on an ambiguous `restrict` name, classical decidability for filters, a reflexive inequality, and a disjoint-filter goal. The corrected module compiles with warnings treated as errors. The finite examples illustrate the theorem and do not replace its countable proof.

The first root negative-control rehearsal used an incomplete local namespace object directory. Lean resolved that directory before the predecessor path and could not import `Variation`. That rehearsal failed and none of those import failures was accepted as a negative-control success. A complete development object tree fixed the path issue. The seven finite controls then rejected with their stipulated mathematical diagnostics, and the divergent-budget control did likewise.

The code review found the arbitrary-gate extension correctly used outer measure, but the draft guide had not explained that distinction. The guide and assumption table now distinguish arbitrary gates from measurable probability events. The inherited `docs/NEXT_BLOCK.md` also still pointed to Core 7.3. Its historical copy is retained and the current restart is corrected to 8.1.

## Initial cumulative gate failure and correction

Both first cumulative gates compiled all 59 production modules, passed the source-facing API and axiom checks, and replayed all 58 substantive modules successfully. They then failed the required diagnostic contract for the inherited `WrongJointPosterior` negative fixture. The expanded aggregate imports made the unqualified `normalize` name ambiguous in its `norm_num` list. A name-resolution error is not acceptable evidence that the intended false mathematical assertion was rejected.

The fixture now explicitly refers to `Instrument.normalize`. Its mathematical assertion and its required diagnostics are unchanged. The predecessor fixture text and full failed receipts are retained. A complete 135-fixture rehearsal checks the correction and the remaining import-sensitive tests before the final successful gates. The failed gate source snapshot, both failed reports and both supervisor exits are under `evidence/failed13_attempt01`. These failures were not converted into successful checks or omitted from delivery.

## Verification contract

Release status comes only from `evidence/RELEASE_RESULTS_BLOCK13.md` and its completed current-source receipts. Both complete gates compile all local production modules in empty object directories, check source-facing API statements, inspect elaborated declarations, audit transitive axioms, replay substantive modules through `leanchecker`, and verify exact rejection contracts. The source snapshot is separately extracted for the second gate. Every production object must match byte for byte.

The unchanged foundation allowlist is `propext`, `Classical.choice`, and `Quot.sound`. The internal compiler memory limit is now 4,096 MiB. There is no claim of a separately enforced process memory cap. The per-command timeout is 45 seconds and the supervisor permits 900 seconds for a complete gate. The actual adapter hash joins the upstream artifact audit.

Prior blocks recorded differing nonproduction `Audit.olean` files despite matching source and axiom output. The current comparison reports its own actual outcome. No explanation is presumed and production equality has no exception.

## Assurance boundary

All 56 predecessor substantive modules and the reviewed source book are unchanged. The probability law, actual event meaning and conditional validity remain mathematical application contracts. Deterministic checks are not statistical samples. No evaluator calibration, model learning, data-dependent error-spending rule, independent proof kernel, upstream dependency rebuild, Windows execution or hosted publication is claimed. The runtime is external to this package.
