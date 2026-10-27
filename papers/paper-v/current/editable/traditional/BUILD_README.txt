PAPER V — TRADITIONAL MONOGRAPH BUILD
20 October 2026 | 130 pages

Build: python3 build.py
Compile-only replay: python3 build.py --check-only
Requires Python 3, XeLaTeX, BibTeX and packages declared by the source. Externally installed
fonts and the full companion tree are copied to an isolated staging directory.
Four XeLaTeX passes resolve references, contents and bibliography. No builder
installs dependencies or executes Lean or mathematical tests.

The authored Paper_V_Traditional_Final.tex is the current source. Historical
assembly snapshots describe earlier layouts and must not overwrite it.
All 83 proof bodies and 118 numbered environments are preserved. The remaining background record is the documented square-wave Gibbs clarification.
The 32 original figures remain, four with presentation repairs. Three exact
Python models and the 40-plate atlas are included. Portable figure generators
and model reports are in this directory.

Preservation and page locators: python3 audit_and_crosswalk.py
Requires PyMuPDF. Physical pages are identified from final PDF page labels,
not an assumed printed-page-plus-one offset. Body page 1 begins at physical
page 9 after the cover and Roman frontmatter. Root package rebuild command:
  python3 scripts/build_pdfs.py --check-only --report /tmp/paper-v-build.json
Run that command from the package root. After edits, rebuild, inspect the
rendered pages, refresh both guides and current metadata, then the manifest.
