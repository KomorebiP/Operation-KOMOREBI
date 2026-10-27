# Visual appendix for Paper IX

A 30-page reader guide with 28 deterministic vector plates. Every illustrated arithmetic calculation uses exact integers, rational numbers, symbolic polynomials, or an explicitly bounded modular enumeration. TikZ coordinates are expository placement, not embeddings of a p-adic metric.

## Rebuild

```text
python Run-PaperIX.py examples
python Run-PaperIX.py appendix
```

Run these from the bundle root, or use `python visual_appendix/build.py --output-dir <new directory>`. The builder regenerates all plates, checks them against the shipped TikZ, typesets twice, appends the resulting pages to the unchanged original PDF, adds source-line navigation, and checks the text and 72-dpi rendering of every assembled page. It never invokes Lean.

The exact checker records 214 named positive assertions, including finite sweeps containing 30,987 case evaluations, and rejects 19 deliberately false controls. A sweep is not counted as many new theorems. The script records its tested ranges and non-claims in `checks/EXACT_CHECKS.json`.

## File guide

`appendix.tex` supplies layout and macros. `source/pages.tex` supplies the full text. `source/models.py` implements two independent Euler coefficient constructions, finite differences, exact valuations, residue maps, correction fibers, and scalar root lifting. `source/generate_graphics.py` uses those models to write `graphics/*.tex`; `drawing.py` contains generic vector drawing helpers. `build.py` performs isolated compilation and PDF assembly.

## Python dependencies

The tested versions are recorded in `editorial_evidence/appendix_build/BUILD_AUDIT.json`. A compatible installation needs SymPy, PyMuPDF, and pypdf; requirements are in `requirements.txt`. The arithmetic model itself uses the standard library. The checks add SymPy for symbolic comparisons. Plotting does not require an image-generation service or a network.

## TeX dependencies

An installed TeX Live with `pdflatex` and article, geometry, fontenc, lmodern, microtype, amsmath, amssymb, mathtools, graphicx, array, booktabs, tabularx, multicol, xcolor, TikZ/PGF, tcolorbox, fancyhdr, hyperref, and bookmark. These are system dependencies, not files copied into the package. Raw font files are not redistributed.

## Boundaries

These examples neither rerun the saved Lean proofs nor resolve the manuscript's remaining singular persistence, presentation, global descent, or exact-valuation questions. The isometry and analytic-root pages distinguish finite residue calculations from the general completeness/analyticity theorems. Exact infinite conclusions are attributed to the numbered source statements, not inferred from sampled grids.
