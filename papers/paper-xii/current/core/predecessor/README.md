# Paper XII — final companion edition

**Komorebi P. · 6 October 2026**

*Patching Support, Hecke Packets, and Conditional Automorphic Completion*

The final collection contains the complete traditional paper, a standalone worked visual guide, and a Lean guide with exact source contracts and catalogs. There is no page limit. All supporting Markdown (`.md`) files are included in this archive; each PDF carries that note.

| Companion | Final PDF | Editable entry point |
|---|---|---|
| Traditional paper | `papers/Paper_XII_Traditional_Final.pdf` | `editable/traditional/Paper_XII_Traditional_Final.tex` |
| Visual guide | `papers/Paper_XII_Visual_Guide_Final.pdf` | `editable/visual_guide/Paper_XII_Visual_Guide_Final.tex` |
| Lean guide | `papers/Paper_XII_Lean_Guide_Final.pdf` | `editable/lean_guide/Paper_XII_Lean_Guide_Final.tex` |

The inherited v0.17.1 release records 49/49 complete **revised internal claims**. Its distinct original-wording ledger records 41 complete, seven partial, and one unchecked. The eight amendments and final publication clarifications are documented individually. Arithmetic realization and propagation require the stated inputs at the actual eigensystem; universal companion existence is not asserted.

The traditional paper retains all 52 proof environments. Original and authoritative revised sources, both historical formal replay records, all production Lean sources, exact vector figures, finite-check programs, logs, and Markdown notes are preserved. Read `RELEASE_SCOPE.md` for the mathematical and evidence boundaries and `SUPPLEMENTARY_INDEX.md` for every included Markdown file.

## Rebuild and verify

Install the prerequisites stated in each editable companion's README. Run commands from this archive's root:

```bash
python3 scripts/build_pdfs.py --check-only --report /tmp/paper_xii_rebuild.json
python3 scripts/check_scope.py
python3 scripts/validate_saved_runs.py --root . --output /tmp/paper_xii_saved_runs.json
python3 scripts/verify_integrity.py
```

The PDF rebuild regenerates the exact visual examples and vector figures. It performs no Lean compilation. Saved-run validation rechecks recorded input/output hashes without repeating the mathematical experiments. `verification/computation/README.md` gives prospective bounded Python and pinned Lean replay commands; fresh experiments should use a disposable copy and a new run identifier. Historical absolute paths in logs document the actual runs; entry points use the relocated archive structure.

A fresh Lean replay was unavailable because the pinned runtime was absent. The preserved Lean records are inherited evidence, separately authenticated by source, object, log and record hashes. The compiler and Mathlib runtime kit is a separate prerequisite, not a hidden part of this archive.

`EDITION.json` records the final PDF sizes, hashes, page counts and evidence census. `MANIFEST_SHA256.json` covers every shipped file. Papers I–XI retain their previous completed content.
