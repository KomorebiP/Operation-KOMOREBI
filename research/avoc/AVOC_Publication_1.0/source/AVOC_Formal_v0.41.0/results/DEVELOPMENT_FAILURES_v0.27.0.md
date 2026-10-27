# AVOC v0.27.0 — development failures and repairs

All failures below are distinguished from the final successful proof and execution evidence.

1. An interactive container session request was unavailable (`StreamingExecNotEnabledContainerError`). Ordinary bounded commands were used instead. No asynchronous completion claim relied on that session.
2. The first semantic-algebra structure used reserved field name `variable`. Lean rejected it. The field is now `atom`.
3. Boolean-operation parser precedence and definitional reduction caused early semantic equations to fail. Explicit functions and parenthesized expressions fixed them. The signature enumeration's literal length proof required a higher local recursion limit.
4. Direct `rfl` did not close every natural-number accounting normalization; appropriate simp/omega proofs replaced it.
5. The first JSON loader proof used an unsuitable monadic simplification and an incorrectly indented return. An explicit match yielded the checked parser/import witness. The zero-cost counterexample needed its node equality exposed before omega.
6. A separate optional source embedded the entire concrete 256-row table and attempted `checkBank rows = true` via ordinary `by decide`. It exceeded a 30-second process cap, was killed, and produced NO theorem certificate. This attempt remains unsuccessful. The source is preserved as `results/v0.27.0/experiments/KernelTableProbe.lean.txt`; the exact failure record is `kernel_table_probe.json`. It is not included in the positive source inventory. No native_decide, admitted proof, or native axiom was substituted.
7. An outer negative-test batch was interrupted before an unfinished record was available. That target and remaining negatives were rerun; all final 71 records have substantive mathematical rejection and no timeout. An initial combined tool call also ended before the cold-producer record existed. A dedicated cold-generator rerun completed and is the only one counted.
8. The concrete bank was accepted by the ACTUAL EXECUTED proved Lean importer, and a fresh inherited Lean producer exported the same 256 programs as the independent Python producer. This does not change the failed standalone-kernel-reduction status in item 6.

The final local library and full audit pass. Pinning and source hashes distinguish their final inputs from early failed drafts. The wrapper/store tests include intentionally invalid inputs and one controlled publication exception. Expected semantic rejection is not classified as a development bug, and no process-kill/power-failure experiment is asserted for the new store.

9. The first final collector interpreted the cold-producer record's source hash as the entrypoint hash; it actually identifies `AVOC/SemanticSynthesisRuntime.lean`. The mismatched interpretation was rejected, corrected to the recorded source, and collection rerun. Neither producer source changed.
