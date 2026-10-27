# Paper III — 1.0.0-rc1 private scoped release candidate

**Do not describe this as a fully Lean-closed or publicly licensed Paper III release.** The original mathematical readers and previous accepted kernel evidence are preserved, with newly proved Section 17 ordinary mathematics. This is a defensible frozen technical handoff, not an unrestricted formal-completion certificate.

## Read first

- `publication/Paper_III_Integrated_Reading_Edition_v1.0.0_rc1.pdf` — 180 pages, with five bookmarks.
- `metadata/RELEASE_NOTES_v1.0.0_rc1.md` — accepted proof scope, new work and known blockers.
- `metadata/PROGRESS_LEDGER_v1.0.0_rc1.md` — exact completed tasks and restart point.
- `metadata/MANUSCRIPT_STATEMENT_REGISTER_v1.0.0.json` — all 167 source-authenticated statement environments.
- `metadata/FAILURES_AND_LIMITATIONS.md` — unrecovered source, external runtime, license, and compiler status.
- `docs/Paper_III_Section17_Analytic_Closeout.pdf` — five-page ordinary proof supplement, including the stronger range norm estimate.

## Verify a fresh extraction

```sh
python VERIFY_RELEASE.py
cd checkpoint_v0.3.0
python tools/verify_manifest.py
```

## Reproduce the new exact tests

Run from the root directory, in an environment with SymPy installed:

```sh
python tests/test_higher_packet_calculus.py
python checkpoint_v0.3.0/tests/section17/exact_section17.py --output /tmp/p3_section17_replay.json
python checkpoint_v0.3.0/tools/exact_packet_checks.py --output /tmp/p3_section16_replay.json
python tests/verify_inherited_formal_evidence.py
python tests/build_statement_register.py
```

The test scripts were written for this package's extracted layout. They can also be run using paths in the source working directory. The 15,331, 2,622 and 677 result receipts are included in `evidence/`.

## Lean reproduction

The Lean 4.34.0-rc2 runtime and nine pinned dependencies are not bundled. Their exact identities are recorded in `checkpoint_v0.3.0/verification/RUNTIME_IDENTITY.json` and `RUNTIME_ARCHIVE.json`. Recover the seven external toolchain chunks and use the original `checkpoint_v0.3.0/README.md` commands for historical core replay. Two new Section 17 candidate modules live in `checkpoint_v0.3.0/formal/drafts/`. They are **not** accepted, not imported, and not counted in this release.

The 16 October edited visual guide is preserved in `provenance/unverified_oct16_visual` for transparency but is not the selected guide. Its 2,693-declaration completion claim has not been authenticated.

## Licensing

See `metadata/LICENSING.md`. No public copying or code license is chosen. Public GitHub release remains gated by an author decision. No font source files are distributed.
