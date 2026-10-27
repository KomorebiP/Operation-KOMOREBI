# Development incidents — v0.3.0

These are developmental failures, not accepted proof evidence.

1. The initial TailSignature check ran before the base compiler process had produced CompletionConsequences.olean and failed with a missing import. The module did not require the topological layer, so its import was narrowed to PairedPrimes and Sections. All inherited modules and the final entrypoint were subsequently rebuilt cleanly.
2. Several rewrites encountered semireducible subgroup/typeclass-instance mismatches. Explicit types and the same controlled transparency option used elsewhere in this development resolved those elaboration failures. No mathematical hypothesis was weakened.
3. An early full SelectorClassification call exceeded the container call's execution window. A repeated bounded development run exited with code 137 while an attempted `rfl` expanded a subgroup-equality transport. The source was isolated in short probes. Replacing that attempted definitional reduction with Mathlib's proved `AddEquiv.addSubgroupCongr_apply` lemma made the complete module compile promptly. The exact external cause of signal 137 was not independently established. No failed or interrupted attempt is counted as verification.
4. D-valued homomorphism constructors initially inferred the wrong subtype for a congruence argument. Explicit source subtype annotations fixed the constructor proof. An overly recursive `ext` was replaced by the exact two extensionality steps required.
5. Warnings-as-errors rejected redundant simp arguments and an unnecessary simpa. Explicit rational-denominator evaluation also needed Rat.den_inv rather than raw decision reduction. These proof-script and test-script failures were corrected without changing the statements.
6. The six new negative controls intentionally fail. Their intended diagnostics and separate positive mathematical witnesses are recorded in tests/controls.json. They are not imported by production.

The preserved logs and source hashes are in verification/development. Small prefix probes used during isolation are preserved under verification/development/probes. The first container timeout ended before its capture helper could write a normal structured receipt; this paragraph records that limitation rather than inventing a receipt.
