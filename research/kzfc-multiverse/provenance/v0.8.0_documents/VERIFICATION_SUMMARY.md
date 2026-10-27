# Completed verification v0.8.0

Status: PASS
Session: 5f7b9e53-c361-42b1-bbff-03d08ac11a39
Theorem declarations audited: 378
Recorded compiler commands: 73, all expected outcomes matched.
Root build: 1234 jobs including pinned dependencies.
Predecessor mathematical modules preserved: 26.
New theorem declarations: 88, including supporting and interpretation lemmas.
Observed axioms: Classical.choice, Quot.sound, propext.

The runtime was restored from the supplied seven parts. The completed compressed-stream hash matches the expected value. The initial longer restore, baseline build and two larger audit batches hit enclosing host limits. They were not treated as completed verification. The final hash-pinned staged session contains every required compiler outcome, including the expected rejection of a false proof and a proof placeholder. Its completion record has exit status zero.

The source scan, all-theorem audit coverage, proof-input equality and predecessor equality checks passed. The pinned dependency cache is trusted and was not rebuilt. Separate archive integrity checking verifies the shipped bytes and manifest, not Lean soundness independently.
