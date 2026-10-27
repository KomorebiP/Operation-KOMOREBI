# Paper XII — final traditional edition

**Patching Support, Hecke Packets, and Conditional Automorphic Completion**  
Komorebi P. — 6 October 2026.

Open `Paper_XII_Traditional_Final.pdf`. The corresponding `.tex`, `.bib`, and generated `.bbl` are included, together with eighteen exact vector PDF figures. Supporting Markdown (`.md`) files are included: `PUBLICATION_NOTE.md`, `FORMAL_EVIDENCE_BOUNDARY.md`, `CLAIM_CROSSWALK.md`, `CURRENT_STATUS.md`, `EDITORIAL_CHANGES.md`, and `SOURCE_PRESERVATION.md`. They distinguish the preserved formal record, present editorial corrections, and conditional arithmetic inputs.

## Portable isolated build

Run with Python 3.9 or later from any working directory:

```bash
python /absolute/path/to/traditional/build.py --output-dir /absolute/path/to/new-empty-output
```

The output directory must be new or empty. The script copies only declared inputs into a temporary isolated build directory, compiles with shell escape disabled, regenerates the bibliography, resolves citations and cross-references, and removes the temporary compiler directory. It produces the PDF, bibliography output, UTF-8 extracted text, logs, PDF information and a SHA-256/page-count report. It never reads scratch font paths or writes intermediates beside the manuscript.

Linux prerequisites: Python 3, pdfLaTeX/BibTeX from TeX Live, Latin Modern fonts, AMS and the listed LaTeX packages, and Poppler's `pdftotext` and `pdfinfo`. On Debian/Ubuntu the corresponding packages are `python3`, `texlive-latex-base`, `texlive-latex-recommended`, `texlive-latex-extra`, `texlive-fonts-recommended`, `lmodern`, and `poppler-utils`. The source uses TeX-distributed fonts and all used PDF fonts are embedded; no fonts under `/tmp` are required. Native Windows behavior is not asserted.

For a byte-identical rebuild use the same TeX Live, package and font versions. The build fixes `SOURCE_DATE_EPOCH=1791244800` (6 October 2026, 00:00:00 UTC), `FORCE_SOURCE_DATE=1`, UTC locale/time settings, and suppresses the volatile PDF trailer ID. Two isolated builds in this environment are compared by PDF bytes, extracted text, page count, and per-page rendered pixels. The accompanying preflight record reports the inspected scope and result.

The figure PDFs are the exact supplied Python-generated vector figures. No AI-generated visual assets were used. All original and revised proof-source snapshots are preserved. Temporary build directories are excluded from the deliverable.
