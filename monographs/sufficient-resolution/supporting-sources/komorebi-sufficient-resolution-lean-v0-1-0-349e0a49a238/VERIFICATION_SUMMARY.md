# Verification summary — Komorebi Sufficient Resolution v0.1.0

- Six production proof modules and one import root rebuilt from source.
- 68 explicit theorem declarations, including helpers and examples.
- 98 explicitly named declarations checked against the standard-axiom allowlist.
- All six production modules replayed using Lean's own kernel via leanchecker.
- False statement and placeholder controls rejected.
- Deliberate custom axiom accepted by the compiler but rejected by the audit allowlist.
- Five exact rational sanity checks passed separately from the universal proofs.
- The source archive was extracted into a second directory, its own compiled
  modules were deleted, and the complete verification was repeated successfully.
- Before/after hashes match for every execution input in both runs. The final
  ZIP contains the same Lean source snapshot; only verification/documentation
  records were added after the extracted-source check.

Trust boundary: the same Lean kernel is used for compilation and replay. Imported
Lean/Mathlib proof artifacts are reused, not independently reconstructed or checked
with a separate proof-kernel implementation. No claim of literature novelty is made.

See `verification/release/report.json` and `verification/roundtrip/report.json`.
