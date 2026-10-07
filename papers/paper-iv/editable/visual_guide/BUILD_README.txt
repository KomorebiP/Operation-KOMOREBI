Paper IV: Visual Guide - Final Companion Edition
Author: Komorebi P.
Edition: 5 October 2026

This folder is a standalone editable source for the 28-page visual guide:
a cover, a reading-route page, and 26 worked pages containing 24 vector figures.

Build the PDF:
    python build.py

Test the build without changing the delivered PDF:
    python build.py --check-only

Use another output directory:
    python build.py --output-dir /path/to/output

The builder runs three pdflatex passes in an isolated temporary copy. A TeX
installation with Latin Modern, TikZ/PGF, tcolorbox, amsmath, geometry, hyperref,
bookmark, fancyhdr, microtype, tabularx and the other packages named in the TeX
preamble is required. No shell escape is used. Python 3 is sufficient for PDF
assembly. SymPy and mpmath are not needed to compile the preserved TikZ plates.

Mathematical checks and model-driven regeneration are separate operations:
    python checks/verify_examples.py
    python source/generate_graphics.py

Those operations require the packages listed in requirements.txt and write
reports or figures. Run them in a temporary copy to retain the delivered
sources and inherited evidence unchanged. No dependency is downloaded by
these scripts. Never infer a fresh mathematical check from a successful PDF
build. The package's verification report records exact execution scope.

Source provenance:
    source/pages.tex                 Preserved original worked prose
    source/pages_final.tex           Updated references and evidence wording
    source/models.py                 Preserved mathematical models
    source/generate_graphics.py      Preserved deterministic plate generator
    graphics/*.tex                  24 preserved editable vector figures
    checks/EXACT_CHECKS.json         Inherited named checks and rational bounds
    SOURCE_IDENTITY.json             Byte identity with recovered source files
    MATHEMATICS_PRESERVATION.json    Formula and figure-call preservation
    EDITORIAL_CHANGES.json           Exact local prose changes and scope
    VISUAL_CROSSWALK.json            Final traditional statement/page references
    EVIDENCE_WORDING.json            Verbatim edition evidence wording

The guide compiles independently of the traditional paper. To reproduce the
editorial transformations after changing a traditional locator map, run:
    python regenerate_editorial.py --traditional-map /path/to/canonical_label_to_final.json --traditional-tex /path/to/Paper_IV_Traditional_Final.tex --evidence EVIDENCE_WORDING.json

To render every page for visual quality review, use:
    python qa_pdf.py

The QA helper requires PyMuPDF and Pillow. It checks page bounds and internal
links, renders every page, and creates contact sheets. Rendering does not by
itself verify the mathematical content.

All 52 displayed formulas, 275 inline mathematical spans, and 24 figure calls
in the worked pages remain unchanged. Model and figure source bytes are also
preserved. Exact identities and rational enclosures retain their stated finite
scope. Curves, moment-share bars, and asymptotic diagnostics are numerical
displays. The four cubic brackets certify local existence and uniqueness only.
