# Building the worked visual appendix

This directory contains the complete editable appendix. Its mathematical source is independent of the preserved original Python implementation, which allows several comparisons to use independently written exact examples.

## Files

- `appendix.tex`: typography and document wrapper.
- `source/pages.tex`: all 24 explanatory pages, formulas, captions, source references, and limitations.
- `source/models.py`: exact integer, rational, finite-ring, matrix, and symbolic models.
- `source/generate_graphics.py`: creates the 22 TikZ plates from those models.
- `graphics/*.tex`: shipped, editable vector plates.
- `checks/verify_examples.py`: 118 named tests with explicit domains or finite ranges.
- `checks/EXACT_CHECKS.json`: the saved successful record, with the model-source hash and the scope of each test.
- `build.py`: isolated example check, graphics regeneration, two-pass LaTeX build, PDF assembly, navigation, and audit.

## Dependencies

Python 3.10+ with `requirements.txt`. For TeX, `pdflatex` must be on PATH, with these packages available:

```
geometry fontenc lmodern microtype amsmath amssymb mathtools
 graphicx array booktabs tabularx multicol xcolor tikz tcolorbox
 fancyhdr hyperref bookmark
```

The TikZ libraries are `arrows.meta`, `decorations.pathreplacing`, `patterns`, and `calc`. No shell-escape or external rendering service is used. No font files are included in the archive.

From the bundle root:

```sh
python Run-PaperII.py examples
python Run-PaperII.py build --output-dir rebuilt
```

Or invoke `build.py` directly:

```sh
python visual_appendix/build.py --output-dir rebuilt
```

The builder checks the source manuscript, runs the exact examples in a temporary copy, regenerates the plates, compiles twice, and appends the new pages. It verifies all pages' text and rendered appearance after assembly. It also checks source-line links, bookmarks, absence of raster image objects in the appendix, page bounds, and LaTeX diagnostics. Every command and its exit code is recorded.

The builder expects the present 24-page layout. An intentional pagination change needs a corresponding update to `APPENDIX_PAGES` and `SOURCE_PAGES`. It fails on accidental overflow to an additional page rather than silently producing the wrong navigation.

To regenerate editable plates after changing a model, run `python source/generate_graphics.py` in a development copy of this directory. Then run the builder. The builder deliberately fails if regenerated plates differ from the shipped `graphics/` tree. Do not edit only an image while leaving its generating model inconsistent.

## Arithmetic and interpretation

The finite Fourier example is in F7, while the coefficient-only parity example is valid in F2. Matrix inverses modulo 32 are checked on both sides. Congruence-fiber pictures enumerate entire specified finite domains. Resolvent examples use rational spectral parameters outside the displayed poles. The eight Smith-chart points are algebraic; only page placement is rendered numerically.

Some checks confirm a finite sample of a general identity explained in the text. The JSON records that bound. Such a pass must not be reported as a new universal proof or Lean certification. Zero-weight graph loops, noncoprime address constraints, inadmissible Smith targets, unavailable denominator inverses, and resolvent poles are retained as explicit boundary examples.
