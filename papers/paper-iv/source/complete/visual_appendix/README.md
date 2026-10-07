# Paper IV visual appendix

A 26-page mathematical reading companion to the later proofread v1.0.0 manuscript.
It adds examples and reader structure; it does not alter theorem statements or proof sources.

## Page sequence

1. Three views: coefficients, reciprocals, zero orbits.
2. Object atlas and factorial normalization.
3–6. Root filters, cyclic product, the signed shift, quotient multiplication.
7–8. Hypergeometric parameters and exact fourth-power orbit reduction.
9–12. Reciprocal inversion, Bell partitions, Newton determinant, Riccati equations.
13–16. Logarithm branches, different reciprocal families, Appell operators, theta coupling.
17–20. Exponent polygon, two-term cubic model, certified local brackets, zero counting.
21–24. Canonical products, finite Fredholm compression, moments, pole asymptotics, zero zetas.
25. One closed order-four calculation: coefficient 69 and tangent coefficient 34.
26. Evidence, formal scope, and open questions.

## Build

```sh
python build.py --output-dir ../rebuilt
```

Python requirements: SymPy, mpmath, PyMuPDF, pypdf. Exact tested versions are listed
in `requirements.txt`; no package is silently downloaded by these tools.

LaTeX uses `pdflatex` with geometry, fontenc, lmodern, microtype, amsmath, amssymb,
mathtools, graphicx, array, booktabs, tabularx, multicol, xcolor, TikZ, tcolorbox,
fancyhdr, hyperref, and bookmark. Installed TeX Live supplies them in the tested environment.
No shell escape is needed. The build copies sources to a temporary directory.

`source/models.py` uses ordinary coefficients in the reduced variable w. It converts
to block-EGF coefficients explicitly. SymPy supplies rational polynomial algebra;
Python Fraction supplies interval arithmetic. mpmath supplies root suggestions and
plot coordinates, never bracket acceptance. The exact checker independently bounds
Taylor remainders and derivatives at rational arguments.

`source/generate_graphics.py` writes editable TikZ plates from those models.
TikZ coordinates for smooth functions are sampled numerical displays; captions state
this. Exact values and interval bounds are exported in `checks/EXACT_CHECKS.json`.

The final PDF has no raster image objects. Integration copies every original page
without editing its content and adds source links only on the appendix pages.

## Mathematical boundaries

No Lean build, universal zero-positivity theorem, new zeta functional equation,
or complete complex-zero census is claimed. The inherited analytic theorems retain
all their original hypotheses. The rational certificates refer to four isolated
positive real intervals, not all roots. See V-26 and `../provenance/`.
