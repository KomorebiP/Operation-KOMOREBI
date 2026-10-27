# Komorebi Physics
## Continuum, Geometry and Refinement

Open `Komorebi_Physics.pdf` for the complete book: **572 pages**, comprising one unnumbered cover, seven preliminary pages numbered i–vii, and 564 pages numbered 1–564. The twelve-page `Komorebi_Physics_Design_Preview.pdf` retains the selected pages' printed folios. The seven research themes, five visual atlases, numerical figures, and established typography are preserved.

The current free-field extension has accepted Lean proofs for the bounded centered operator, graph convergence on the complete maximal Hamiltonian domain, actual resolvents at every nonreal spectral parameter, and quadratic error bounds under a finite third-order Fourier moment. The abstract spectral-functional-calculus API identification remains open. These results concern a fixed infinite Fourier space; they do not close the sampled-grid, interacting-field, or cosmological production problems.

## Package map

- `source/`: editable LaTeX, styles, figure assets, and retained scientific data.
- `compiled/`: eighteen component PDFs and final TeX logs.
- `book/`: front matter, reading text, assembly specification, page map, and navigation validation.
- `audit/`: current publication QA, complete-book renders, source-preservation review, and earlier editorial records.
- `formal/continuum/`: the integrated Lean project, precise replay instructions, controls, declaration audit, and current and failed verification records.
- `reference_record/`: unchanged earlier computation and provenance records.
- `history/publication_v0.50.0-g1_metadata/`: the preceding README, release reports, and package manifest, preserved as history.

Original material is licensed under `LICENSE`; third-party rights remain unchanged. Historical filenames and counts identify earlier checkpoints and are not relabelled as new checks.

## Rebuild the publication

Required: Python dependencies from `requirements.txt`; XeLaTeX, PDFLaTeX, and `kpsewhich`; the packages imported by the preambles; and separately installed URW Base35 OpenType, Latin Modern, TeX Gyre Type 1, and Palatino-compatible mathematical fonts. No font files are redistributed in this package.

The XeLaTeX sources use `source/monographs/font-location.tex`, whose Linux default is `/usr/share/fonts/opentype/urw-base35/`. The outer-book script locates TeX Gyre Pagella and Heros metrics and programs with `kpsewhich`.

From the package directory:

```text
python3 build_documents.py
python3 assemble_reading_volume.py
python3 audit_design.py
python3 render_design_audit.py
python3 tools/build_design_preview.py
```

The first command makes three passes per component and accepts filename substrings for a partial rebuild. Assembly preserves vector pages and rebuilds internal destinations. The audit checks final logs, text bounds, fonts and navigation. PDFium renders every book page. The current scoped preservation comparison is `audit/source_preservation_centered.json`; the inherited generic baseline-comparison mode intentionally does not accept the two reviewed hypothesis clarifications in this update.

To regenerate only the current verification-scope schematic:

```text
python3 tools/render_formal_scope.py --publication-root . --accepted-proof-record formal/continuum/verification/block51/current/receipt.json
```

This schematic is separate from numerical figure generation. Layout reproduction requires compatible TeX and font versions; byte-identical cross-platform output is not promised. Document builds do not rerun Lean or scientific experiments. The retained atlas generator references an original-tree `evidence/figure_checks.json` that is absent from this publication copy. That omission and the historical reproduction limitations remain explicit.

## Replay the formal extension

Read `formal/continuum/README.md`. Restore the exact portable Lean 4.34.0-rc2 runtime externally; it is not bundled in the source ZIP. From `formal/continuum`, run:

```text
python3 verification/block51/current/snapshot/runner/verify_centered.py --project . --runtime /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --controls CONTROL_MANIFEST.json --out-dir /absolute/path/to/a-new-verification-directory
```

The output directory must be new. Preserve the pinned compiler and dependency identities. The accepted receipt is `formal/continuum/verification/block51/current/receipt.json`, with status `PASS_SCOPED_CENTERED_EXTENSION`.

The accepted run compiled 26 local targets through 64 recorded commands, audited 209 environment declarations (162 new plus 47 generator), completed five module kernel replays, and passed 21 controls: eight positive, twelve elaboration rejections, and one custom-axiom policy rejection. The four new modules contain 74 explicit theorems, 15 definitions and 11 abbreviations; generated auxiliaries explain the larger environment count. Source, objects and relevant runtime identities remained stable.

These checks reuse pinned external compiled dependencies and the same Lean kernel. They do not rebuild the compiler or all Mathlib, provide an independent proof assistant, or certify every historical physics module. Failed attempts remain in the record.

## Publication verification boundary

Five affected component documents were rebuilt. All 572 book pages rendered successfully, with valid bookmarks and internal destinations. All 107 original explicit proof bodies, 157 source data files, and numerical image assets are unchanged. Exactly two original theorem-like statements add the explicit hypothesis `T >= 0` for a compact-time envelope/supremum. The nonzero-spacing and third-order-moment hypotheses and the coefficient `1/6` remain unchanged. Only the verification-scope diagram changed among the image assets.

The five numerical suites belong to the preceding publication checkpoint; they were not rerun for this formal extension. The production-energy obstruction remains in the book. This is a focused formal-extension and publication audit, not an independent line-by-line review of every chapter or bibliography.

See `RELEASE_VERIFICATION.md`, `RELEASE_VERIFICATION.json`, `audit/continuum_publication_qa.json`, and `formal/continuum/PROGRESS_LEDGER_v0.51.0.md` for the accepted scope and remaining work. The final package manifest records identity, not mathematical validity.
