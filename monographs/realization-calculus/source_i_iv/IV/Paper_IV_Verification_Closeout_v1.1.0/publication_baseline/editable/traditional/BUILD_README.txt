PAPER IV — TRADITIONAL MONOGRAPH
8 October 2026

Build: python3 build.py
Compile-only replay: python3 build.py --check-only
Requires Python 3, XeLaTeX, BibTeX and the packages declared by the TeX source.
Bundled relative fonts and the full source tree are copied into isolated
staging. Four XeLaTeX passes resolve the bibliography, contents and references.
No mathematical or Lean checker runs during PDF compilation.

The current TeX is the authored source. The prior assembly script is archived
under provenance/pre_monograph_metadata and describes an earlier layout.

Generate the six Python figures: python3 generate_monograph_figures.py
Requires NumPy and Matplotlib. Exact models and finite ranges are recorded in
FIGURE_MODELS.json. The 26-plate atlas uses deterministic source-native figures.

Verify canonical preservation and locators: python3 audit_and_crosswalk.py
Requires PyMuPDF and preserves all 95 numbered environments and 68 proof bodies.
After any source edit, rebuild, review the rendered pages, refresh crosswalks
in both guides, metadata and the package manifest. Current QA is under
qa/monograph/ and verification/monograph_traditional_report.json.
