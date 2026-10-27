# Paper I visual appendix

Author: Komorebi P.  
Formal source: Paper I v1.2.1, unchanged.

The 22 pages develop exact examples of fixed operator grammars, seed rank,
quotient obstructions, typed spaces, oblique packet coordinates, transfer
composition and cancellation, support closure, conjugacy, semisimple row
budgets, primary extraction, paths and cycles, coordinate-ring normal forms,
bilateral-shift completion, residue carries, invariant-hull iteration and the
algebraic tensor bound.

## Editable source

- `appendix.tex`: page design and mathematical macros.
- `source/pages.tex`: all 22 expository pages, equations and source references.
- `source/models.py`: exact rational/symbolic mathematical objects.
- `source/generate_graphics.py`: deterministic generation of the 20 TikZ plates.
- `graphics/*.tex`: the generated vector plates, also directly editable.
- `checks/verify_examples.py`: 96 exact checks and their explicit ranges.
- `build.py`: isolated rebuild, PDF assembly, navigation and preservation checks.

Install the Python dependencies in `requirements.txt`. The TeX installation
must provide pdfLaTeX, Latin Modern, microtype, amsmath, amssymb, mathtools,
graphicx, array, booktabs, tabularx, multicol, xcolor, TikZ, tcolorbox,
fancyhdr, hyperref and bookmark. These system packages are not bundled.

From the complete bundle's root:

```text
python Run-PaperI.py examples
python Run-PaperI.py appendix
```

Outputs go to `rebuilt/`, not to the shipped source or reading directories.
The builder works in a temporary directory. No Lean command is called.
The source-date epoch is fixed unless the caller supplies another value.

## Navigation

The combined PDF has separate manuscript and appendix outline groups. The
appendix's V-number links navigate among concept pages. In the combined PDF,
click the gray source line below any appendix title to return to the relevant
manuscript passage. The standalone appendix's manuscript references remain
printed citations, because it does not contain the main paper.

## Interpretation

All new matrix ranks and polynomial identities are checked with exact
arithmetic. The path sample range is 1 through 12; the cycle sample range is
3 through 12. The manuscript's all-size results are cited separately. The
finite shift window illustrates an infinite sequence, not a periodic array.
No example is promoted to a newly Lean-checked theorem. Existing figures in
the main 40-page paper are preserved, not replaced.
