# Paper VII visual appendix

This appendix is authored in LaTeX with deterministic Python-generated TikZ.
There is no image-generation dependency and no raster artwork in the new pages.
Every plate remains editable. The current 28 pages contain 26 plates plus an
object atlas and an evidence guide.

## Sources

- `appendix.tex`: fonts, page style, mathematical macros and bookmarks.
- `source/pages.tex`: the complete exposition and mathematical formulas.
- `source/models.py`: exact finite matrices, channel/code models, symbolic
  projector families, rational sine enclosures and convention definitions.
- `source/generate_graphics.py`: generates `graphics/*.tex` and `INDEX.json`.
- `checks/verify_examples.py`: positive assertions and rejected false controls.
- `checks/EXACT_CHECKS.json`: saved result from the delivered source.
- `build.py`: temporary-directory build, merge, source links and preservation audit.

## Build

From the bundle root:

```text
python Run-PaperVII.py examples
python Run-PaperVII.py build
```

Install the packages in `requirements.txt` into an appropriate Python environment
when needed. For the original numerical companion use its `pyproject.toml` or
`requirements-tested.txt` at bundle root. The tested versions are recorded in the
actual audit; Python 3.10+ is the syntax target.

The LaTeX build needs `pdflatex`, T1 Latin Modern, microtype, AMS math, mathtools,
graphicx, array, booktabs, tabularx, multicol, xcolor, TikZ/PGF (arrows.meta, calc,
patterns, decorations.pathreplacing), tcolorbox, fancyhdr, hyperref and bookmark.
No external BibTeX step is needed for the new appendix; its references are precise
links to the preserved manuscript/supplement and their original bibliography.

The original manuscript needs three LaTeX passes from a clean directory because
its contents and lists occupy multiple pages. Two passes leave stale page numbers
in those lists. The original replay tool performs all three.

The build pins SOURCE_DATE_EPOCH for stable document dates. Binary PDF equality
across TeX versions is not claimed. Replays compare the exact source and the
rendered/textual output in the tested environment. The combined PDF begins with
25 original pages and seven completion-supplement pages; the appendix starts at
physical page 33 and has its own V- page labels.
