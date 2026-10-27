# Release Manifest

## Manuscript

- `paper/Projector_Resolved_Seed_Calculus_I.pdf` — final 40-page v1.2.1 paper.
- `paper/Projector_Resolved_Seed_Calculus_I.tex` — complete source with local bibliography.
- `paper/figures/` — ten generated figures in PDF and PNG formats.

## Executable evidence

- `code/python/seed_calculus/` — Python companion library v1.1.1.
- `code/python/tests/` — 18 automated tests.
- `code/python/run_all.py` — regenerates results, figures, CSV summary, and run record.
- `code/python/dist/projector_seed_calculus-1.1.1-py3-none-any.whl` — installable wheel.
- `formalization/lean/` — source-only Lean theorem-completion component v1.0.1 with pinned toolchain and dependencies.
- `formalization/lean/LEAN_THEOREM_MAP_v1.0.1.md` — exact 35-row, 84-declaration manuscript map with scope and exclusions.
- `formalization/lean/scripts/verify_theorem_map.py` — executable fail-closed map/API consistency checker.
- `results/` — JSON/CSV certificates and captured verification logs.

## Provenance and release control

- `provenance/Source_and_Claim_Map.md` — proof/evidence boundary.
- `provenance/Lean_Completion_Contract.md` — the frozen 35-row v1.2.1 completion criterion.
- `provenance/Verification_Notes.md` — final build and inspection report.
- `provenance/Verification_Render.png` — contact-sheet audit of every paper page.
- `provenance/Paper_I_Audit_Ledger_v0.1.0.md` — preserved historical audit of v1.0.0.
- `README.md`, `CHANGELOG.md`, `RELEASE.json`, `REPRODUCIBILITY.md` — release documentation.
- `CITATION.cff`, `CITATION.bib` — citation metadata.
- `LICENSE_STATUS.md` — explicit no-license-selected notice.
- `Run_All.ps1`, `Run_All.sh` — non-mutating end-to-end verification runners for Windows and Unix-like systems.
- `SHA256SUMS.txt` — sorted member checksum manifest, excluding itself.

The archive checksum is distributed outside the ZIP as `Projector_Resolved_Seed_Calculus_I_v1.2.1.zip.sha256`.
