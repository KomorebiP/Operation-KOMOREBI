# Paper XI — visual guide source, reading release 1.0.0

This directory belongs to Publication Block 07, 10 October 2026. Use the coordinated builder at the release root. The current readers are the 109-page monograph, 53-page core visual guide and 235-page Lean/evidence guide. They accompany the preserved 77-page research paper v0.4.0 and 36-page atlas v0.5.0.

## Build

From the release root run `python tools/build_readers.py --output ../paper_xi_build`. Output must be outside the package. The compatibility entry point `python build.py --output-dir /absolute/external/output` invokes the same coordinated builder. All three originals must be built before assembling cross-document links.

XeLaTeX, pdfLaTeX, BibTeX (or bibtex.original), PyMuPDF, fontconfig and installed URW/DejaVu fonts are required. No font files are distributed. Pass `--font-dir` to select a local URW OTF directory. Shell escape remains disabled. The preserved research PDFs are copied, not regenerated from unavailable Block 02 sources.

## Source and evidence boundaries

The main proof/statement bodies and all selected Lean sources, excerpts and scientific figures are unchanged. Block 07 restores44 malformed superscript expressions in nine construction appendices against15 original Markdown notes. It also clarifies that one table column measures the source representation carrier, not its symplectic quotient. The earlier Appendix D field-degree factor correction is retained. See `evidence/block07` at the release root for exact patches and hashes.

Older source catalogs, review logs and summaries remain historical records. Their dates, page counts and hashes identify their original checkpoints. Current receipts are in `verification/block07`. Immediate baseline sources are in `predecessor/block06/publication/source`; older originals remain deeper in that unchanged predecessor tree.

Rebuilding these PDFs is not a Lean build. The missing full Block 02 editable archive, missing terminal v0.45 receipt and access-limited Henniart–Lemaire reread remain explicit. See the root ledger and RELEASE_SCOPE.md.
