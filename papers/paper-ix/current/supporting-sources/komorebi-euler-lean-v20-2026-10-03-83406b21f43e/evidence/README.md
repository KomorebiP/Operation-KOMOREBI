# Verification evidence

`baseline/` is the fresh replay of the incoming 483-declaration project.
`v19_replay1/` and `v19_replay2/` are successful clean 566-declaration builds.
The second replay used a separate mathematical source-tree copy. Per-module
logs, source hashes, axiom reports and timings are retained in each directory.
Compiled build trees are omitted from the source release; their verified
cross-replay hashes are in `clean_replay_comparison.json`.

`development/` contains failed and successful development logs, including API
probes. They are not final verification outputs. No probe source or unfinished
mathematical declaration is accepted in the source project.

`terminal_alignment.json` is supplementary exact integer/rational corroboration,
not the basis for any universal theorem. `input_manifest_verification.json` and
`inherited_source_preservation.json` record provenance, not proof checking.
