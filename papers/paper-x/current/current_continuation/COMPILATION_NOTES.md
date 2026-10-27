# Compiler evidence and resolved attempts

The release's successful status is determined by strict compiler exit codes and matching source/proof-object hashes. Empty logs and the existence of an older proof object are not treated as a pass. The independent audit recompiles the new sources against verified predecessor objects.

Retained failures include:

- The first weighted residue proof applications repeatedly hit Lean elaboration limits. An independent small statement-only check passed; the exact reduction hotspot was not isolated. Refactoring the proof through abstract finite-index estimate predicates resolved the applications without changing the hypotheses. The successful attempt9 source/object pair was restored after an optional cleanup attempt was interrupted.
- Early residue-norm and signed-norm attempts required corrected coercions, quotient APIs, explicit arguments, and strict linter syntax. All production modules must have a later strict successful record before inclusion in the final manifest.
- `NormResidueWeightedCounting` initially failed concrete Euclidean-space instance inference, with a later timeout in the same proof. Opening the classical scope resolved the compilation; `coordinator_c_NormResidueWeightedCounting.json` records the successful source and object.
- `NormResidueGeneratorAttachment` initially lacked the point-sum import and the Euclidean namespace. Both were corrected; the successful record is `generator_bridge_b_NormResidueGeneratorAttachment.json`.
- The exact weighted torsion attachment required corrections to finite enumeration and equivalence transport. Its bound consumer used an unavailable inequality helper, replaced by an explicit ordered-ring proof. Their unique verification records identify the final successful versions.
- `NormSignPartition` required explicit scalar-membership arguments and the strict linter's preferred local-instance syntax. Its second attempt passed. The actual generator-sum recombination then passed on its first attempt.
- The final arithmetic assembly initially needed its already-derived finite quotient enumeration activated locally when rewriting the canonical count. The correction retains the same finite quotient and theorem hypotheses; its later compiler record determines the final status.

Some historical `norm_filter_attempt` log names were reused by two author lanes. They are retained as incomplete development history and are not the definitive evidence for either final module. Unique later compiler records and the independent audit establish those final versions.

Two earlier independent audit processes were interrupted while the build load was being reduced. Their exit130 records remain in the audit history; later completed replays determine their final status. Other cancellation requests arrived after a compiler had already completed. Those records retain the actual completion exit code, rather than being described as interruptions.

The negative compiler controls are intentionally false statements or a placeholder. Their expected rejection is separate from production compilation. The unsigned-congruence control first failed before reducing to the validator's required `False` goal; its corrected control reaches the intended contradiction. Both versions are retained.

See `verification.json`, the per-module records, route reports, and the independent audit for final coverage. Archive hash verification checks file integrity and is not described as another Lean compiler run.
