Paper IV Lean Guide — final companion edition, 5 October 2026
Author: Komorebi P.

Read Paper_IV_Lean_Guide_Final.pdf.

The guide covers the complete v1.0.0 formal release: 68 full scoped manuscript
results, 151 additive map rows, 1,164 exact mapped declarations (953 theorems and
211 constructions), 119 Lean files, and the saved explicit kernel audit. The
formal execution evidence is inherited from 5 September 2026. No fresh Lean
build was run to produce this edition.

Contents
- Eight tutorial chapters explain coefficient filters, normalization, analytic
  realization, zero geometry, products, determinant and zeta models, pole
  estimates, all nine final closure modules, and reproduction.
- 49 source-exact excerpts retain full selected declarations and proofs.
- Complete 68-result ledger and 151-row declaration catalog with all target
  names, source locations, kinds, and manuscript labels.
- Complete direct-import inventory, nine dependency pins, traditional locators.

Compile only
  python3 build.py
Requires Python 3 and XeLaTeX. The document fonts are P052 OpenType (Roman,
Bold, Italic and BoldItalic), DejaVu Sans, DejaVu Sans Mono, and Latin Modern
Math. The P052 files are explicitly selected by their .otf filenames through
TeX's normal font search. No absolute workspace or runtime font path is used.
The builder makes four passes, clearing stale aux/toc/out first. It does not
run Lean, regenerate data, fetch dependencies, or alter the canonical source.

Optional static-data regeneration
  python3 build_guide_data.py --source /path/to/PRSC_IV --traditional /path/to/traditional
The defaults fit this edition's editable/lean_guide directory. This command
verifies canonical source checksums and generates catalogs, excerpts, pins,
and navigation. It does not invoke Lean. The original source is read-only.

Evidence
  generated/static_audit.json         Current static reconciliation
  generated/excerpts.json             Original file/line/hash provenance
  generated/theorem_map.json          All rows and exact target names
  generated/inherited_axiom_records.json  Saved transcript records
  generated/completion_ledger.json    68 full scoped manuscript results
  generated/dependency_pins.json      Full pinned package objects
  generated/imports.json              Every source module's direct imports
  generated/traditional_crosswalk_provenance.json  Locator source hash
  qa/pdf_checks.json                  Current PDF structural/text checks
  qa/visual_review.json               All-page visual review record
  qa/clean_rebuild.json               Isolated compile-only replay
  PROOFREAD_REPORT.txt                Editorial self-review and limits

The raw .lean.txt excerpts preserve original UTF-8 source bytes for their line
intervals. The .render.txt copies escape only display syntax and route selected
mathematical glyphs to the math font. Excerpts retain their original module
context; they are not standalone compilation units. All source files and the
original release gate are included elsewhere in the full edition package.

No license is added by this guide. The canonical source's license-status file
and assistance disclosure remain authoritative.
