# Development failures and retained boundaries — v0.9

5 recorded draft Lean module checks returned nonzero before correction.
Their exact diagnostics, source hashes and failed source snapshots are retained in
`evidence/development/` and indexed in `evidence/DEVELOPMENT_ATTEMPTS.json`.

1. CostedPrimitives: gcd symmetry/recursion rewriting and an unnecessary tactic after
   simplification failed. The testValue empty-word lemma also required explicit
   simplification across an inherited exposed module definition.
2. CostedLattice: dependent-induction generalization warnings, a normalize-name
   collision, and a locally let-bound gcd positivity obligation failed. Arithmetic
   polynomial rearrangements were proved explicitly rather than assumed.
3. CostedDiscovery: the EchelonBackend namespace had not been opened, so required
   definitions were initially unresolved. The accepted module uses the actual
   inherited state invariant and loop definitions.
4. CostedExamples: attempting decidable equality of the entire Option Basis value
   failed because the proof-carrying recursive type has no automatic DecidableEq.
   The zero-fuel identity is definitional and was proved by rfl instead.
5. First CostedComputed16 export: the local logical-certificate namespace was not
   open. The exporter was corrected and regenerated before the accepted cold run.

Two enclosing development dependency commands were interrupted after partial
successful compilation. Their completed source-checked artifacts were used only
for subsequent development. They are not counted as complete audits. A new empty
local build directory was used for the final audit.

The five saved runtime chunks were hashed, streamed through XZ, and restored
successfully. Their working copies were removed only after restoration, to conserve
disk space; source Library files were not modified. No runtime/font files are
shipped in this release.

The final 79-task cold audit completed without a failed or timed-out
accepted task. All seven deliberately false/placeholder controls rejected and the
positive control accepted. The Python audit completed without test failure. Any
later extraction/packaging failure is recorded in the separate replay report and
must not be counted as a successful full replay.

Packaging correction: the first outer filename was incorrectly shortened to v0.zip
by pathlib.with_suffix, which treated .9 as a suffix. The path construction was
corrected to append .zip, then the final archive was rebuilt and rechecked. This
was a packaging-name error, not a proof or numerical failure. The shortened
working artifact was removed rather than delivered.
