Paper VII — Final traditional, visual and Lean companions
Komorebi P. · 6 October 2026 (UTC)

Start with papers/Paper_VII_Traditional_Final.pdf. The complete corrected finite
manuscript, the full strengthened mathematical development, and all substantive
mathematical sections of the six completion supplements appear together.

papers/Paper_VII_Visual_Guide_Final.pdf contains 40 worked pages: the 28 original
pages and 12 further examples. All 26 original and 12 added editable vector
plates are provided. papers/Paper_VII_Lean_Guide_Final.pdf teaches the actual
formal source, its 19-item result scope, all 323 named declarations, six
constructed objects, 25 modules, dependency pins and replay procedure.

EDITION.json gives final page counts and file hashes. COMPANION_MAP.json points
to the precise result, proof, page, source and excerpt crosswalks. The detailed
correction and evidence scope is in CORRECTIONS_AND_SCOPE.txt and audit/.

The complete editable sources are under editable/. Both untouched recovery ZIPs
are under downloads/, and all 784 untouched extracted files are under source/.
Historical sources and records are preserved, even when a later theorem or
correction supersedes an earlier description.

Rebuild and compare all three PDFs from this package root:
  python scripts/build_pdfs.py --check-only --report /path/to/rebuild_report.json

This needs Python, PyMuPDF, a working TeX installation with pdflatex, bibtex and
xelatex, and the fonts/packages named in the editable sources. No dependencies
are downloaded by the builders. Each companion is built in a temporary folder;
page counts, extracted text and complete PDF bytes are compared separately.
Omit --check-only to replace the shipped PDFs after a successful build. Such a
replacement intentionally changes the file-integrity state if its bytes differ.

Verify every shipped file's size and SHA-256:
  python scripts/verify_integrity.py

Available finite computational replay, to new output directories:
  python verification/scripts/reproduce.py --source source --downloads downloads --out /path/to/raw_replay
  python verification/scripts/reproduce_corrected.py --source source --downloads downloads --out /path/to/corrected_replay
  python verification/tools/validate_manifest.py /path/to/raw_replay/manifest.json --root .
  python verification/tools/validate_manifest.py /path/to/corrected_replay/manifest.json --root .

The numerical replay needs the exact external libraries described in the audit.
The independent rational examples need only Python's standard library. Commands
for the inherited formal development require the separately supplied pinned
portable compiler kit; consult the Lean guide. No new Lean compilation or
original SymPy-suite execution was performed for this edition.

Papers I–VI retain their preceding records. Paper VII is now closed in the three
requested companion formats. Papers VIII–XII remain frozen.
