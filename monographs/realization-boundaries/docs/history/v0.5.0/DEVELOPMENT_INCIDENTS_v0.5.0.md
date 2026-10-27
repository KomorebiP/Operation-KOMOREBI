# Development incidents — v0.5.0

All entries here are failed or corrected development steps, not accepted proof evidence.

1. The container rejected allocation of an interactive terminal session. The command had not created its helper file; an attempted ordinary invocation reported that the file was missing. The helper was recreated with an ordinary command, and the five archived chunks were combined, hash-checked, and extracted successfully.
2. `AddSubgroup.closure_le` takes an explicit target subgroup before returning an equivalence. Draft calls using `.mpr` without that argument failed. `(AddSubgroup.closure_le _).mpr` is the checked API.
3. The pinned finite-set witness lemma is named `exists_notMem`, not `exists_not_mem`.
4. Countability inference through `pairedGroup` did not unfold the wrapper automatically. The new instances use the already checked `paired_countably_infinite` theorem, rather than assuming countability.
5. A canonical profinite additive group does not automatically expose an `AddCommGroup` instance. The generation definitions and transport lemmas need only `AddGroup`, so their general signatures were broadened accordingly. No assumption of commutativity was inserted.
6. Warnings promoted to errors rejected unnecessary simplification and a proof-valued `letI`. The proof terms were adjusted to the accepted style.
7. The eta-image comparison did not simplify through the paired-group abbreviation automatically. Applying the existing exact `profiniteCompletionEquiv_eta` theorem resolved the type-level wrapper explicitly.

Failed compiler outputs and source hashes are retained in `verification/development`. The final run deletes all generated project objects and rebuilds every production module before audits, controls and replay. The accepted run has no failed gate.
