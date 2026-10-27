Paper VI traditional final edition, 5 October 2026
Author: Komorebi P.

Build the assembled source with:
  python3 build.py
Reassemble from preserved branches and explicit changes, then build with:
  python3 build.py --assemble

After the PDF is complete, regenerate semantic/physical locators with:
  python3 audit_and_crosswalk.py
Render every page and create contact sheets with:
  python3 review_pdf.py

Requirements: Python3; pdflatex, bibtex and the TeX packages already named in the preamble. The optional crosswalk/render scripts use PyMuPDF and Pillow. No dependency installation is performed by these scripts.

All builds run in this folder. Figures are packaged in core_figures and extension_figures. Source snapshots and the explicit JSON change ledger permit reconstruction. SOURCE_DATE_EPOCH fixes ordinary PDF date metadata. The TeX document is self-contained apart from its figures and references.bib.

The traditional paper includes no new Lean compilation claim. Its33-result formal scope and compiler counts are inherited and dated. PartsII andIII do not receive automatic formal certification.
