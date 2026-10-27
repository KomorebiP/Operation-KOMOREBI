# Paper X visual appendix

Thirty typeset concept pages with 28 deterministic editable TikZ plates. This is an
expository layer, not a new formal proof release. The latest inherited status is
17 checked / 3 partial.

## Exact models

`source/models.py` implements explicit integer, rational, polynomial and finite-field
models. `checks/verify_examples.py` checks 263 positive assertions and rejects 14 false
controls. The report lists every assertion and its bounds. Finite checks do not replace
the prose arguments for infinite branches, closedness or analytic integral convergence.

`source/generate_graphics.py` generates the complete plate set from those objects. Floating
coordinates are used only to place graphical marks. No image generator is involved.
`source/pages.tex` is the editable exposition. The main preamble is `appendix.tex`.

The scalar norm examples take place in F5[u]/(u^2-2). They do not prove all number-field
norm-character bounds or supply prescribed Frobenius primes. The positive count-growth
exponent of x^2=0 describes finite thickenings, not a multiplicity of complete roots.

## Build without mutating evidence

```bash
python ../Run-PaperX.py appendix --output-dir ../new_appendix_build
```

This runs exact checks, regenerates TikZ, compiles two LaTeX passes, assembles the 80-page
reading edition, installs 30 source-page links, and compares each assembled page's text
and 72-dpi rendered appearance to its input. It checks the absence of raster figure
objects in the appendix, missing references and overflowing boxes. It never invokes Lean.

The appendix's internal page references work in both PDFs. The gray “Main text:” line
links to the corresponding manuscript section in the combined edition. References to
newer continuation notes are printed as such; the full source files remain in the bundle.

Python dependencies are pinned in the root requirements file. TeX packages include
geometry, fontenc, lmodern, microtype, amsmath, amssymb, mathtools, mathrsfs, bm, graphicx,
array, booktabs, tabularx, multicol, xcolor, TikZ, tcolorbox, fancyhdr, hyperref and bookmark.
No font binaries or software installations are distributed.
