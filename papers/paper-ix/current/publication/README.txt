Paper IX publication entry points, 10 October 2026

The three final PDFs are in publication/pdfs. Identical copies are in output/pdf.
RELEASE.json is the current document/page/hash register. Previous metadata is
retained in verification/2026-10-10/predecessor_files.

Use python rebuild_pdfs.py from the root for an isolated copied-source rebuild.
It requires installed TeX and fonts, downloads nothing, and does not run Lean.
The low-level build_publication.py starts each selected generated-output directory
from scratch, reports build failures through its exit status, and must not be
confused with a theorem compiler.

For deliberate manuscript edits, build main and visual, run
python tools/refresh_navigation.py, then build the Lean guide. This changes the
reading edition and invalidates its old manifest; it is not an automatic renewal
of the mathematical or formal audits. See the root README and final review.
