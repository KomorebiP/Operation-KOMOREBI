# Paper XI — traditional source, synchronized v0.6.0

This editable directory belongs to Publication Block 06 (10 October 2026).
The numbered mathematical statements, construction appendices, selected Lean source, raw excerpts and scientific figures retain the predecessor's source identities except where explicitly listed in the Block 06 change report. The changes are reader wording, front matter, cross-document navigation and build dependencies, not new arithmetic existence proofs.

## Build

From the checkpoint root, run `python tools/build_readers.py --output /absolute/new-output`.
The output must be outside the checkpoint. The compatibility command `python build.py --output-dir /absolute/new-output` in this directory invokes that same coordinated build. All three readers are built together so their direct page links can be resolved.

XeLaTeX, pdfLaTeX, BibTeX (or bibtex.original), PyMuPDF and installed URW/DejaVu fonts are required. The builder discovers the local URW OTF directory with fontconfig; pass `--font-dir` when necessary. No font files are included. Generated font lookup TeX stays in the external build directory. Shell escape is disabled. The build uses preserved PDF figure assets; it does not rerun the figure generators, a Lean compiler or arithmetic matrix constructors.

## Historical files

JSON source catalogs, declaration catalogs, excerpt metadata, and any older BUILD_REPORT, SUMMARY or FINAL_SUMMARY files in this directory are unchanged historical records. Their dates, page counts and hashes refer to that original edition, not the new PDF. Current receipts are under `verification/block06`. Original wrappers and drivers are byte-preserved in `predecessor/block05/baseline/core_readers_editable`.

The complete Block 2 editable archive, terminal v0.45 compilation receipt and previously limited classical-input reread remain disclosed gaps. The current mathematical obligations are in PROGRESS_LEDGER.md at the checkpoint root.
