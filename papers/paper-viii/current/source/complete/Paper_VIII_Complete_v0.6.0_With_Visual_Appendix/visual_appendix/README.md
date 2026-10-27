# Visual appendix for Paper VIII

The appendix is a worked reader guide, not a replacement manuscript or a new formalization release. It has 28 pages and 26 deterministic vector plates. All matrices, costs, and finite choices come from the models under `source/`; the figure generator writes editable TikZ, not raster illustrations.

## Rebuild

From the bundle root:

```text
python Run-PaperVIII.py examples
python Run-PaperVIII.py appendix
```

Or run `python visual_appendix/build.py --output-dir rebuilt/appendix` directly. The builder runs the exact checks, regenerates the plates, typesets twice, assembles the PDFs, installs source links, and verifies page text/render preservation. It does not invoke Lean. It requires `pdflatex` on PATH and the Python dependencies below. All builds use a temporary directory.

## Sources

- `appendix.tex`: typesetting definitions and page design.
- `source/pages.tex`: full expository text, examples, captions, and manuscript references.
- `source/models.py`: rational, symbolic, and finite-enumeration models.
- `source/drawing.py`, `source/generate_graphics.py`: deterministic TikZ production. Smooth coordinates sample explicit formulas; their floating approximations are drawing coordinates, not exact proofs.
- `graphics/*.tex`: 26 editable vector plates.
- `checks/verify_examples.py`: 190 positive assertions and 11 rejected false controls.
- `checks/EXACT_CHECKS.json`: recorded exact outcomes, named checks, source hashes, and displayed values.
- `build.py`: safe isolated build and PDF assembly with 81-page preservation checks.

## TeX dependencies

Tested with pdfTeX/TeX Live 2025. The appendix uses article, geometry, fontenc, lmodern, microtype, amsmath, amssymb, mathtools, graphicx, array, booktabs, tabularx, multicol, xcolor, TikZ/PGF, tcolorbox, fancyhdr, hyperref, and bookmark. The original manuscript additionally uses the installed aomart class and its dependencies. Raw font files are not included.

## Evidence boundaries

The 56-item finite register belongs to the saved v0.6.0 formal source, not to the new appendix examples. The supplement constructs the actual compact ranges and proves best-rank/tail results from supplied ordered-SVD equations. This is separate from SVD existence or verification of numerical QR/SVD. Four classical manuscript entries remain separately tracked. Original benchmark values remain historical; all timing examples introduced in the appendix are explicitly synthetic.
