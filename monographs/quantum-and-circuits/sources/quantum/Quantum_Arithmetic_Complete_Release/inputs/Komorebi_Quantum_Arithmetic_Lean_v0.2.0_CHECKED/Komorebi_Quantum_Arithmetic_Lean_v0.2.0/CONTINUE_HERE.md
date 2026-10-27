# Continue from the checked version 0.2.0

Treat this archive as the authoritative successor to the uncompiled 0.1.0 draft.
Do not substitute historical files from `history` for active source.

First run:

    python scripts/verify_lean.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2

Read `STATUS.md`, `PROOF_BOUNDARY.md`, `THEOREM_INDEX.md`,
`DEVELOPMENT_FAILURES.md`, and the final verification JSON before editing.
Preserve all 22 original theorem statements and the full checked development.
A timeout is unresolved and is never a successful negative test.

Possible further formalization targets are the explicit Matrix identity relating
P to F D F.conjTranspose, Matrix action on the normalized signed and unsigned
states, and the arbitrary-modulus character/projector theorem. These are further
targets, not claims of this release. Any publication badge should use the bounded
wording in `PUBLICATION_STATUS_TEXT.md` until those additional links are proved.

The reusable portable runtime is identified in `RESTORE_RUNTIME.md`. No network
installation is required when the existing archived kit is restored.
