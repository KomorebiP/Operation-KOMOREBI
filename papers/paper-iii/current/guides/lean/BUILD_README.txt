PAPER III: LEAN GUIDE PDF BUILD

Compile the authored guide from this directory:

    python3 build.py

Write compiled files to another directory:

    python3 build.py --output-directory /path/to/output

Compile without changing delivered files:

    python3 build.py --check-only

The alias --output-dir is also accepted. Python 3.9 or later, XeLaTeX, and the
packages named in the guide preamble are required. Four XeLaTeX passes run in
an isolated complete source copy. Bundled fonts, styles, chapters, excerpts,
and generated TeX inputs are retained. BibTeX is invoked only if bibliography
data is present. SOURCE_DATE_EPOCH defaults to the edition date and
FORCE_SOURCE_DATE is enabled.

PDF compilation does not regenerate guide data, edit formal sources, or invoke
Lean. The source/map/transcript reconciliation workflow remains separate.
The package-level scripts/build_pdfs.py --check-only compares extracted page
text and page counts against the shipped PDFs and requires PyMuPDF.

BUILD_NOTES.txt preserves the earlier authoring and verification record.
