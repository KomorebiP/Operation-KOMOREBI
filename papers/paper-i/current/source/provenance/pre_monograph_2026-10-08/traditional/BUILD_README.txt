Paper I traditional edition: portable source rebuild

Run:
  python build.py
Optional fresh exact-example checks:
  python build.py --check-examples

The final LaTeX source is complete. No original archive or network access is
needed for this rebuild. pdflatex and ordinary TeX Live packages are required:
article, lmodern, microtype, AMS math, mathtools, geometry, aliascnt, booktabs,
longtable, tabularx, enumitem, fancyhdr, hyperref, cleveref, xcolor, setspace,
tcolorbox, needspace, multicol, makecell, graphicx, TikZ, titlesec, bookmark,
and caption. Python example checks additionally require SymPy.

PDF build logs go to build_logs/. The checker writes
visual_checks/EXACT_CHECKS.json and does not perform a Lean build.

assemble_traditional.py records the editorial integration. In a release
bundle it reads preserved sources from ../../source/. To use a collected
source tree instead, supply --source-collection PATH. It regenerates the
editable source and incorporates the two documented hypothesis corrections.
Do not rerun the assembler after making manual editorial changes unless the
same changes have been incorporated into its generation logic.

The optional review_final.py renderer requires PyMuPDF and Pillow. It produces
contact sheets and a machine-readable layout report. The TeX source rebuild
itself does not require those packages. The additional tocloft package is
used for the compact, linked table of contents.
