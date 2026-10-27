# Block 05 — Development failures and repairs

This is a record of actual failed attempts, not a list of unresolved active admissions. The source snapshots, compiler outputs and receipts are under `verification/development/block05/`. The authoritative cumulative proof result is `verification/final/report.json`.

## Restoration and baseline

The compiler was not initially mounted. All seven existing portable-runtime parts were located, their checksums and assembled payload were verified by the original assembler, and the pinned kit was extracted. A first attempted interactive container session was rejected because streaming execution is unsupported; it did not run the assembler or change any proof. The ordinary process-based invocation then completed. `verification/block04_baseline/report.json` records the successful fresh baseline compilation/audit at 304 theorems, 372 names and 23 negative controls.

## Failed development compilations

There are **9 failed development compilations** among **17 development receipts**. These failures are preserved as failures; later successful revisions do not relabel them.

| Snapshot | Module | Outcome |
|---|---|---|
| `20260913T194322617398Z` | `LindbladJumps` | Compiler exit 1; source and diagnostic retained |
| `20260913T194351843254Z` | `LindbladJumps` | Compiler exit 1; source and diagnostic retained |
| `20260913T194755639353Z` | `DetailedBalance` | Compiler exit 1; source and diagnostic retained |
| `20260913T195004930509Z` | `DetailedBalance` | Compiler exit 1; source and diagnostic retained |
| `20260913T195226408172Z` | `LindbladDynamics` | Compiler exit 1; source and diagnostic retained |
| `20260913T195702587033Z` | `LindbladCoherence` | Compiler exit 1; source and diagnostic retained |
| `20260913T195846565169Z` | `LindbladExamples` | Compiler exit 1; source and diagnostic retained |
| `20260913T195938842509Z` | `LindbladExamples` | Compiler exit 1; source and diagnostic retained |
| `20260913T200043847706Z` | `LindbladExamples` | Compiler exit 1; source and diagnostic retained |

The repairs addressed obsolete or misnamed simplification lemmas, misplaced `omit` commands, accidental prefix matching while editing a theorem name, finite-matrix versus function application representation, finite-sum and scalar-cast normalization, derivative-function normalization that changed the displayed function, order of explicit theorem arguments, and explicit complex positivity instances. Several otherwise valid proof attempts also failed warnings-as-errors checks for unused variables or unnecessary tactic sequencing. No linter was disabled to bypass those checks.

The principal mathematical clarification is separate from these script/API errors: the source flux-ratio formula needs an explicit zero-rate convention. The conductance form and the active-edge equivalence theorem were proved with the appropriate positive-argument conditions. This is not a failed proof of detailed balance, nor a claim that a zero denominator is valid in ordinary analysis. Exact negative examples document assumptions that cannot be discarded.

The active proof files were repaired without admissions, custom axioms, native-evaluation escapes or kernel bypass. None of the failed snippets enters the cumulative aggregate. The final and freshly extracted runs use single-worker compilation with warnings as errors and the exact pinned imported dependency cache.
