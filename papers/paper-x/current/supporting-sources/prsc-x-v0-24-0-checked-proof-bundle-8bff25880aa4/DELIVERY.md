# Compact delivery of the checked Block 24 proof bundle

This bundle contains the same verified production source and proof-object bytes as the full Block 24 release: all 153 production Lean modules and their compiled proof objects, plus all checks, logs, documentation, and review evidence. No formal source or proof object was changed for this delivery.

The sole omitted payload is the redundant nested predecessor archive:

- Filename: `PRSC_X_v0.23.0_Checked_TwentyThird_Block.zip`
- SHA256: `93d1d13a4dbf8bf71a8d742613c78d7fceff30bb8beb3e0225d438645fd57c70`
- Expected location for full provenance/package-release gates: `references/PRSC_X_v0.23.0_Checked_TwentyThird_Block.zip`

That Block 23 archive was saved with the preceding release and is an external prerequisite for replaying the full provenance and package-release gates that explicitly hash it. Its provenance entry and historical audit references are retained unchanged. Those gates require restoring that exact archive at the path above. Compilation of the delivered Lean modules and the supplied new-module replay do not require the nested archive.

The full archive remains locally available as `PRSC_X_v0.24.0_Checked_TwentyFourth_Block.zip`, size 195,478,312 bytes, SHA256 `f4d50104385c415d28ba4869be7822f1a830f87b7bc0dad62f772f994160442b`. Saving that large archive failed twice at the transfer stage. This smaller delivery avoids resending its nested predecessor history while retaining all current formal work and evidence.

The original full-release `archive_replay.json` remains unchanged. A separate `compact_replay.json` is appended only after successful replay of all three new modules from this compact payload. As in the full release, the replay records the payload hash before final delivery metadata is appended. All delivered source and proof-object hashes remain identical to `verification.json`.

`SHA256SUMS` is regenerated for files actually present in this delivery, including this note and the compact replay metadata. It therefore deliberately does not list the externally retained predecessor archive.

The original audit and release documentation describe the full release. This delivery only adds this note, a prominent README note, updated documentation hashes, and compact replay metadata. The full archive and original working files remain unchanged.
