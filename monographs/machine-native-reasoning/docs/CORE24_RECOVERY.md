# Recovered checkpoint and runtime

The 0.16.1 outer archive supplied in this conversation is 32,424,140 bytes,
not the recorded 35,505,363 bytes. Its SHA-256 is
`82060f864cdbff4de302a500c7ad7fd32652672a452ef42f0eea572bd88e39a2`,
not the recorded final hash. Python's ZIP reader rejects the missing directory.
Intentional rematerialization of the same file returned identical bytes.
The cause of that stored-artifact mismatch is not inferred.

A local-header recovery read every complete member with valid decompression,
CRC, byte length and the retained payload manifest's SHA-256. The interruption
occurs during `evidence/fresh16/objects/MachineTheory/RevisionExamples.olean`.
The earlier embedded `CORE83_FROZEN_SOURCE.zip` is complete and has exactly the
externally recorded hash
`ccd0f26544ab7e8323516974a8ddf6ed4e193ff9f2de292d3ab8fc0b2e94fd6b`.
Its 397 inputs all match the recovered successful `final16/report.json`.
Fourteen payload files were restored from this exact snapshot. In all, 1,412
of the expected 1,477 historical payload files were recovered with exact hashes.
The 65 missing trailing files are listed in the machine-readable recovery record.
The missing historical fresh report, release records and tools are not invented.
The external separately delivered report and receipt remain historical claims;
new complete cumulative gates establish the current source assurance.

The previous frozen source and selected recovered historical records are under
`evidence/history_core83`. The old outer manifest and detailed recovery list are
under `evidence/recovery17`. The full 72-file proof/source preservation contract
is in `PREDECESSOR.json`. The five original source-book files are unmodified.

The runtime is reconstructed from the saved Library files
`Lean_Compact_01.zip` through `Lean_Compact_05.zip`. Concatenating their single
chunk members produces a 2,220,147,424-byte XZ archive with SHA-256
`f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`.
The complete 166,035-member extraction is recorded in
`evidence/recovery17/runtime.json`. The archive checksum is local consistency
with the saved toolchain, not an independent attestation of its source origin.

The pinned compiler is Lean 4.34.0-rc2, commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`. Mathlib is
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The complete gate also checks all
nine repository revisions and every actually imported upstream proof-cache
artifact against the runtime's saved inventory. It does not rebuild all Mathlib.
No runtime or standalone font binary is included in the delivered formal package.
