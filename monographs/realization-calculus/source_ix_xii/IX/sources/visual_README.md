# Final Euler visual companion

The guide is an article-format companion to the main paper and Lean guide. Its
17 pages consist of the title page, contents, and 15 focused mathematical
pages. The 12 figures are vector PDFs. PNG versions are supplied for layout QA.

From the release root, regenerate the exact illustration data and figures:

```bash
python3 sources/generate_figures.py
```

This executes 5,490 bounded exact assertions. Coefficients are formed by
factorial-series reciprocal convolution modulo `2^256` through row 255, with
independent rational ordinary-series inversion through row 12. Every plotted
residue is exact. The universal exponent curves and scale arrays come from the
separately proved theorems; their coordinates are theorem-derived integer
data, not a numerical proof.

The tested domains and all figure/data hashes appear in
`figures/figure_manifest.json`. Its schema-version-1 provenance limits are
explicit: it records the script hash but does not impose machine-readable
resource caps. No randomness is used. Matplotlib and NumPy are used only for
rendering, matrix storage, and page coordinates; the arithmetic assertions use
Python integers and `fractions.Fraction`.

Compile from the `sources` directory, repeating the second command until the
references and contents are stable:

```bash
pdflatex -interaction=nonstopmode -halt-on-error \
  -jobname=Paper_IX_Euler_Visual_Guide_Final visual.tex
pdflatex -interaction=nonstopmode -halt-on-error \
  -jobname=Paper_IX_Euler_Visual_Guide_Final visual.tex
```

The wrapper uses standard TeX Live packages and Latin Modern fonts. Figure
paths in the wrapper body are relative to the `sources` working directory.
The final PDF is delivered at
`output/pdf/Paper_IX_Euler_Visual_Guide_Final.pdf`.

The final layout review is recorded in `audits/VISUAL_GUIDE_QA.json`, with
rendered pages in `audits/visual_pages/` and the contact sheet in
`audits/visual_contact_sheet.png`. The clean final compilation has no
overfull/underfull boxes, duplicate anchors, or undefined references.

The guide explicitly separates inherited Lean coverage of the original
completion and rank-four ordinary-step/metric results from the new generic
prime-power transfer, mixed-step, factorial, and analytic extension. It does
not describe the latter as newly formalized in Lean.
