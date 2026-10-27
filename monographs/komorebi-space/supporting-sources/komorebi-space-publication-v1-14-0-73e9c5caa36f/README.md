# Komorebi Space

**Coherent realizations, obstructions, and descent**  
Komorebi P. · Publication edition 1.14.0 · 14 October 2026

This edition presents the realization calculus as a continuous mathematical work, with companion books for its geometry and its Lean formalization.

## The books

- **Monograph:** definitions, proofs, worked examples, solved problems, hypothesis tables, and a guide to formal coverage.
- **Visual Guide:** sixteen worked visual investigations, with new graphics, parameter changes, and pointers to the monograph's proofs.
- **Lean Guide:** the formal interfaces, representative declarations, theorem hypotheses, and instructions for using the source.

The three PDFs are in `books/`. The LaTeX sources and figure assets are in `source/`. The `lean/` directory contains the formal development; `examples/` contains exact rational Python examples; `tools/` contains the book builder and figure generators. `verification/` records source identity, the accepted verification scope, and the contents of this edition. `SHA256SUMS` covers every other file in this package.

## Mathematical and formal scope

The printed results and formal counterparts have explicit hypotheses. The Lean development contains 160 production modules and four import entrypoints, with 1,846 explicit theorem or lemma declarations and 5,321 exported declarations. All sixteen principal theorem groups on bounded realization, budgets, regularization, and certificates now have formal counterparts. This includes the actual infinite diagonal family and certified tails, the sharp limit over all real budgets, and the exact rounded noisy parameter rate.

These totals count different objects. Exported declarations also include definitions, instances, structure operations, and generated helpers. Formal coverage of the sixteen groups does not assert a separate Lean theorem for every explanation, illustration, or proof route in the monograph.

The edition integrates byte-preserved accepted proofs. The parent verification covered 156 targets and 44 controls. The diagonal completion strictly checked seven added modules and their entrypoint, audited 273 exported declarations, and recorded eight targeted control outcomes. Their exact evidence is retained separately. The release verification records the integrated build and source identities without relabeling the historical controls as a new combined audit.

The monograph retains its written arguments. The Lean guide now develops the diagonal interfaces and explains the full budget limit and rounded noise schedule. The Visual Guide remains a complementary collection of sixteen visual investigations. Detailed command records, failed attempts, and independent reviews accompany the separate **Technical Record**.

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

Komorebi P. *Komorebi Space: Coherent realizations, obstructions, and descent*. Publication edition 1.14.0, 14 October 2026.

The edition number identifies the supplied source and text.
