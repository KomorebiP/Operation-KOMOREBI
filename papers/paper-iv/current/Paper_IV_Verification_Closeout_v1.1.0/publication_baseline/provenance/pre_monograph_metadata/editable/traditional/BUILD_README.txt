PAPER IV — TRADITIONAL FINAL COMPANION
Komorebi P. · 5 October 2026

BUILD THE PDF
  python3 build.py

Requirements: Python 3 and a standard TeX installation providing pdflatex,
bibtex and the packages named in Paper_IV_Traditional_Final.tex.
The build performs one initial TeX pass, BibTeX, and two resolving TeX passes.
It does not install dependencies or execute Lean or mathematical computations.
SOURCE_DATE_EPOCH is fixed and the TeX source suppresses volatile PDF metadata.

RECONSTRUCT THE EDITORIAL SOURCE
  python3 build.py --assemble

This optional step reads source/proofread.tex and writes the final source
through the explicit, asserted replacements in assemble.py. All changes are
listed in EDITORIAL_CHANGES.json. It then compiles the PDF normally.
The unchanged historical strengthened source is retained in source/strengthened.tex.

VERIFY PRESERVATION AND LOCATORS AFTER A BUILD
  python3 audit_and_crosswalk.py
This optional script requires PyMuPDF in addition to Python 3. It checks all
95 selected-source numbered statements and all 68 proof environments are
byte-identical in the final source and writes the label and record locators.
The final traditional numbering is unchanged from the selected source.
Physical PDF page 1 is the unnumbered cover; printed page n is physical page n+1.

LAYOUT REVIEW
  python3 review_pdf.py
This optional rendering helper requires PyMuPDF and Pillow. It renders every
page, creates contact sheets and checks page bounds, replacement glyphs and
the final TeX log. Its automated output must be followed by visual inspection.

EDITION POLICY
The selected September 5 proofread manuscript is the later scoped edition.
It contains all 68 theorem-like records and all 68 proofs of the v1.0.0
manuscript. The earlier strengthened manuscript's functional-calculus section
was deliberately moved outside Paper IV's scope by the later manuscript,
which assigns that subject to Paper VI. Its standard fact and proposition
remain in the unchanged historical source. No Paper VI file was changed.
EDITION_RECONCILIATION.json records every retained, renamed and migrated label.

FORMAL EVIDENCE
This is a traditional companion edition, not a new Lean release. The
manuscript ledger describes the preserved v1.0.0 release, which records
151 map rows, 1164 targets, 953 theorem declarations and 211 constructions.
The imported Standard Fact 11.1 remains imported. Open questions remain open.
No fresh Lean execution is asserted by this PDF build or its layout audit.
