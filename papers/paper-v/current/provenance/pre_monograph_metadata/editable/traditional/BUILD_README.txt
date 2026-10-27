Paper V traditional final edition,5 October 2026,Komorebi P.

Build current source: python3 build.py
Reassemble source from preserved branches and exact editorial ledger recipe: python3 build.py --assemble
Requires Python 3, pdfLaTeX, BibTeX and standard TeX packages. No dependency installation is performed.32 vector figure PDFs and references.bib are local to this directory.
Audit source preservation and regenerate locators: python3 audit_and_crosswalk.py (requires PyMuPDF).
Render all pages and contact sheets: python3 review_pdf.py (requires PyMuPDF and Pillow).
The source contains both full manuscript branches. Part Iuses original section/result numbering; Part IIuses E-prefixed numbering. Physical PDF page=printed page+1 because the unnumbered title cover comes first.
This build typesets preserved mathematical work; it does not compile Lean or rerun numerical experiments. For historical verifier execution use source/complete/original_snapshot from the full handoff package. Fresh verification scope is recorded outside this editable tree.
