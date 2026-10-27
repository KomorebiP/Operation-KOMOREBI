# Independent release-infrastructure review

Reviewed all eleven v0.41 release tools and their current hashes. The 57 isolated helper and schema probes passed. No open release-infrastructure blocker remains in this review.

Three findings were closed before recording the reviewed hashes: mixed parser/crash diagnostics in negative logs, missing import digests in resumable build records, and omitted inherited example-fixture hashes. The final gate also binds negative records to the current Lean executable, rejects empty evidence objects, requires exact recorder experiment sections and counts, and requires review coverage for new AVOC modules even when they declare no named theorem.

The probes used temporary synthetic fixtures under the reviewer output directory and actual helper functions extracted or imported from the reviewed tools. They did not execute production gates or alter source, proof, oracle, or historical evidence. The synthetic accepted oracle schema is a validator control only.

One reviewer-script run failed during JSON serialization of a Python set. The report now serializes a sorted module list, and the complete rerun passed.

This is a practical independent review, not a universal proof of the Python gate implementation or evidence authenticity. A current clean build, full axiom audit, negative suite, bounded executable oracle, inherited regressions, and final release/package checks remain independently required.

The subsequent runtime-provenance gate change was reviewed separately. Fifteen additional isolated probes passed, covering exact transitive RecorderMain source/object membership, missing or stale files, module count, executable identity, and the pinned Lean binary hash. The original 57-case record retains its original tool hashes. The final reviewed tool map now binds the updated gate, for 72 passed probes across both stages.
