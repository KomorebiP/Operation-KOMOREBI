Paper II visual guide — Komorebi P. — 5 October 2026

Compile the final editable guide from this directory:
    python3 build.py

Requirements: Python 3 standard library and pdfLaTeX with the TeX packages
named in the preamble. Figures are local TikZ vector sources. No raster image
generator, network access, Lean compiler, or external Python module is needed
to compile the PDF. Exact PDF bytes may differ across TeX installations.

The guide contains 24 worked pages and 22 exact model figures, preceded by
a cover and reading routes. V1–V24 are stable plate labels, not PDF page
numbers. Traditional-paper references use the printed page numbers.

The preserved model code is in source/models.py; exact figures are generated
by source/generate_graphics.py. checks/verify_examples.py requires SymPy 1.14.0.
Fresh reproduction records and finite tested ranges are in the complete
package under verification/computational/. Original source bytes are retained
under source/visual_guide_original/. The guide is explanatory, with no new
claim of universal computational proof or additional Lean coverage.

The 22 figure sources, models.py, and verify_examples.py are unchanged.
source/pages.tex is the original body. source/pages_final.tex changes the
companion designation, final traditional-paper locators, and the V24 evidence
paragraph. All other worked mathematics is retained. VISUAL_CROSSWALK.json
records the precise source-to-final relationships and final manuscript hash.

The complete package also supplies scripts/regenerate_visual_guide.py:
    python3 scripts/regenerate_visual_guide.py \
      --original source/visual_guide_original \
      --traditional editable/traditional \
      --output editable/visual_guide
Run that command from the complete package root to regenerate the wrapper
and locators. The standalone build.py command is sufficient for normal edits.
