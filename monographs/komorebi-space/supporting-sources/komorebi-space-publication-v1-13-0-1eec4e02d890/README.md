# Komorebi Space

**Coherent realizations, obstructions, and descent**  
Komorebi P. · Publication edition 1.13.0 · 12 October 2026

This edition presents the realization calculus as a continuous mathematical work, with companion books for its geometry and its Lean formalization.

## The books

- **Monograph:** definitions, proofs, worked examples, solved problems, hypothesis tables, and a guide to formal coverage.
- **Visual Guide:** sixteen worked visual investigations, with new graphics, parameter changes, and pointers to the monograph's proofs.
- **Lean Guide:** the formal interfaces, representative declarations, theorem hypotheses, and instructions for using the source.

The three PDFs are in `books/`. The LaTeX sources and figure assets are in `source/`. The `lean/` directory contains the formal development; `examples/` contains exact rational Python examples; `tools/` contains the book builder and figure generators. `verification/` records source identity, the accepted verification scope, and the contents of this edition. `SHA256SUMS` covers every other file in this package.

## Mathematical and formal scope

The printed results and the formal counterparts have explicit hypotheses. The accepted Lean development contains 153 production modules and three roots, with 1,693 explicit theorem or lemma declarations and 5,048 exported declarations. Thirteen of the sixteen principal analytic theorem groups have formal counterparts. The infinite diagonal family and tail bounds, the sharp budget asymptotic, and the rounded noisy diagonal rate are proved in the monograph but have no corresponding Lean instance in this edition.

The production Lean files are unchanged from the accepted verification. This publication revision is editorial; it does not claim a new Lean compilation. The earlier clean verification covered 156 targets and 44 controls. The books distinguish source verification, mathematical explanation, and finite computational examples. Detailed command receipts and development history accompany the separate **Technical Record**.

## Rebuilding the books

With Python 3 and TeX Live installed, run from the package directory:

```sh
python3 tools/build_books.py
```

The script runs three LaTeX passes per book, writes PDFs and logs under `build/books/`, records source hashes, and reports unresolved references or overfull boxes. Individual books can be selected with `--book monograph`, `--book visual`, or `--book lean`. A complete TeX installation must include the packages imported by `source/preamble.tex` and `source/komorebi-publication.sty`.

The supplied figures are ready for the LaTeX build. The five `tools/plot_*.py` programs regenerate the plotted figures using Python, NumPy, and Matplotlib. They write assets into `source/figures/` and reports under `build/figure_reports/`; run them in a working copy if you want to retain the delivered assets unchanged. Diagram sources are in `source/figures/`. Figures are constructed from explicit mathematical formulas and diagram code.

The visual guide has its own figure collection. Regenerate its two groups with:

```sh
python3 tools/visual_companion/foundations.py
python3 tools/visual_companion/analysis.py
```

The guide's page text is recorded in `source/visual_companion/scenes.json`. After editing that text, run `python3 tools/build_visual_companion.py`, then `python3 tools/build_books.py --book visual`. The monograph section pointers are recorded beside the scene file. The visual guide uses new worked examples and visual comparisons; the monograph remains the reference for proofs and general hypotheses.

See `lean/README.md` and `lean/USAGE.md` for the pinned Lean environment and build commands. See `examples/README.md` for the exact rational examples.

## Citation

Komorebi P. *Komorebi Space: Coherent realizations, obstructions, and descent*. Publication edition 1.13.0, 12 October 2026.

The edition number identifies the supplied source and text.
