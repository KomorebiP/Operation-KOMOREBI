# Paper VII Lean and evidence guide

This monograph teaches the unchanged v0.6.0 source through exact contracts and proof walkthroughs. It contains all 19 scoped finite items, all 323 named theorem declarations in 25 modules, 67 exact contiguous source selections and nine dependency pins. Six constructed objects have a separate inherited audit of proof fields. Five physical continuum targets remain open.

The cross-reading tables locate all 19 core items, all 79 proof-bearing strengthened statements and all six retained proof supplements in the final traditional volume. Printed labels and physical PDF pages resolve from that volume's actual page labels. Shared ingredients do not extend formal coverage.

From the package root:

```bash
python editable/lean_guide/build.py
python editable/lean_guide/build.py --output-directory /path/to/pdf_rebuild
python editable/lean_guide/build.py --check-only
```

The builder stages the complete authored source tree in an isolated temporary directory and performs four XeLaTeX passes. It does not regenerate prose, tables, figures, mathematical data or proof evidence. Absolute script paths work from other directories. The output-directory and check-only modes keep delivered products unchanged. Fonts are bundled and resolve through relative paths. Python 3, XeLaTeX and the packages named in the preamble are required.

Source documentation and evidence reconciliation:

```bash
python editable/lean_guide/assemble.py
python editable/lean_guide/static_check.py
python editable/lean_guide/refresh_evidence.py
python editable/lean_guide/navigation.py
python editable/lean_guide/build.py
python editable/lean_guide/verify_pdf.py
```

The first two commands accept `--source PATH` for a relocated snapshot. Assembly needs FontTools, reads the bundled font files, and stops on count, source, inventory or saved axiom mismatches. `refresh_evidence.py` binds the frozen current computation report, checks its expected prose counts and dependency hashes, and accepts `--verification PATH`. It runs no experiment. `navigation.py --map PATH` can refresh cross-reading rows, but it checks the actual traditional PDF identity and page labels before writing them. Updating an edition requires renewed layout review and matching final dependency pins.

Files ending `.lean.txt` preserve exact raw UTF-8. The `.render.txt` files only escape TeX control characters and provide explicit glyph fallback. Every raw selection remains byte-identical to the retrieved guide. Source locations and hashes appear in `generated/excerpts.json` and the printed register. `generated/static_reconciliation.json` binds all 25 modules, 323 targets, inherited axiom logs, transitive imports, nine pins and six constructed-object records. `generated/mathematical_span_preservation.json` protects all 322 delimited mathematical spans and all contract and proof-walk paragraphs in the six teaching chapters.

`qa/pdf_checks.json` records extracted theorem names, exact excerpt checks, glyph and reference checks, text bounds and link bounds. Every page is rendered for visual review, with full-size detail renders of dense code and catalog pages. PDF QA needs PyMuPDF, Pillow and `pdffonts`.

The current 9 October computational report is `verification/monograph_checks/COMPUTATIONAL_REVIEW.json`. It records actual numerical, exact rational, symbolic, verifier-software and deterministic plate executions with their finite scopes, caps and manifest pins. Counts from overlapping gates are not added. The guide's source and PDF checks are documentation evidence.

Kernel execution remains inherited from the 6 September v0.6.0 release. Lean, Lake and Elan are absent on this host. No fresh kernel compilation or deliberate compiler-control execution is claimed. The source snapshot omits portable compiler-kit dependencies and compiled interfaces. See the replay chapter for the original pinned-kit procedure.

`historical_assembly/` preserves the retrieved guide's authoring inputs and historical evidence descriptions. Its dates, page locators and host limitations describe the earlier edition. It is excluded from document builds. Historical AI disclosures in retained source material remain preserved. This authored guide has no active AI disclosure.
