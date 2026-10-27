Paper I: Modern Monograph source rebuild

From this directory, run:
    python3 build.py

The master file is Paper_I_Traditional_Final.tex. Paper_I_Monograph.tex is an
equivalent named entry point. Six chapter files and visual_atlas.tex hold the
editable text. The style is komorebi-monograph.sty. The build uses XeLaTeX,
ordinary TeX Live packages, fontspec, unicode-math and the bundled fonts.
No network or original archive is required.

Optional main figure rebuild, from editable/traditional:
    python3 figure_sources/rebuild_figures.py
This needs NumPy and Matplotlib. Included vector PDFs are used by default.

Optional exact atlas checks, from editable/traditional:
    python3 visual_checks/verify_examples.py
These checks require SymPy. They verify the 96 exact examples described in
the prior monograph report and do not compile Lean.

The current visual repair is described in VISUAL_REPAIR_REPORT.txt. The prior
mathematical corrections are in MONOGRAPH_REVISION_REPORT.txt. Original
traditional sources and figures are retained under source/provenance.
