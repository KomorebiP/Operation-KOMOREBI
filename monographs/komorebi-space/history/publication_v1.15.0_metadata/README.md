# Komorebi Space

**Coherent realizations, obstructions, and descent**  
Komorebi P. · Publication edition 1.15.0 · 15 October 2026

This edition presents the realization calculus as a continuous mathematical work, with companion books for its geometry and its Lean formalization.

## The books

- **Monograph:** definitions, proofs, worked examples, solved problems, hypothesis tables, and a guide to formal coverage.
- **Visual Guide:** sixteen worked visual investigations, with graphics, parameter changes, and pointers to the monograph's proofs.
- **Lean Guide:** the formal interfaces, representative declarations, theorem hypotheses, and instructions for using the source.

The three PDFs are in `books/`. The LaTeX sources and figure assets are in `source/`. The `lean/` directory contains the formal development; `examples/` contains exact rational Python examples; `tools/` contains the book builder and figure generators. `verification/` records source identity, the accepted verification scope, and the contents of this edition. `SHA256SUMS` covers every other file in this package.

## Mathematical and formal scope

The printed results and formal counterparts have explicit hypotheses. The Lean development contains 162 production modules and four import entrypoints, with 1,859 explicit theorem or lemma declarations and 5,339 exported project declarations. All sixteen principal theorem groups on bounded realization, budgets, regularization, and certificates have formal counterparts. This includes the actual infinite diagonal family and certified tails, the sharp limit over all real budgets, and the exact rounded noisy parameter rate.

The declaration inventory also includes definitions, instances, structure operations, and generated helpers, so its exported-declaration total is larger than the explicit theorem count. Formal coverage of the sixteen groups does not assert a separate Lean theorem for every explanation, illustration, or proof route in the monograph.

Two further connections make the printed examples directly accessible in Lean. `DiagonalInexactRate` proves the explicit rate for an inexact solve at the rounded parameter, retaining the measured-data normal-residual hypothesis. `DiagonalRangeObstruction` proves nonclosedness of the actual infinite diagonal range and exhibits a datum in its closure with no preimage. Independent statement reviews compare both results with their printed hypotheses and conclusions.

The monograph retains its written arguments. The Lean guide develops the formal interfaces and explains the full budget limit, rounded noise schedule, and these two connections. The Visual Guide remains a complementary collection of sixteen visual investigations. Detailed command records, failed attempts, and independent reviews accompany the separate **Technical Record**.

## Run an example and verify the library

Start with [WORKED_EXAMPLE.md](examples/WORKED_EXAMPLE.md) for a complete rational correction, its exact expected certificate, the generation and verification commands, and the corresponding mathematical and Lean statements. See [examples/README.md](examples/README.md) for the other finite examples.

After preparing the pinned environment described in [lean/USAGE.md](lean/USAGE.md), run the integrated verifier from the publication root:

```sh
python3 verification/runner/runner.py --output ../verification-v1.15.0-01
```

The accepted integrated replay freshly compiled all 166 project targets and audited all 5,339 exported project declarations. All 56 controls had their specified outcomes: 18 acceptances, 35 elaboration rejections, and three axiom-policy rejections. The receipt binds those results to the recorded sources, compiler, installed dependencies, and generated project objects.

Choose a new output directory outside this package for every attempt. The runner rebuilds the project sources, inventories declarations, checks recursive axiom dependencies, and runs the diagnostic controls. Its `receipt.json` records the outcome. Read [verification/runner/README.md](verification/runner/README.md) for the exact meaning of `PASS`, the trusted environment, and the retained failure records. An ordinary `lake build` provides a separate compilation check.

The earlier audits remain historical evidence: the cumulative parent record covered 156 targets and 44 controls, and the accepted diagonal completion added eight targeted controls and an audit of 273 exported declarations. The integrated runner includes those 52 controls together with four controls for this edition's two added connections.

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

The guide's page text is recorded in `source/visual_companion/scenes.json`. After editing that text, run `python3 tools/build_visual_companion.py`, then `python3 tools/build_books.py --book visual`. The monograph section pointers are recorded beside the scene file. The visual guide uses worked examples and visual comparisons; the monograph remains the reference for proofs and general hypotheses.

See [lean/README.md](lean/README.md) and [lean/USAGE.md](lean/USAGE.md) for the pinned Lean environment, imports, and verification commands.

## Citation

Komorebi P. *Komorebi Space: Coherent realizations, obstructions, and descent*. Publication edition 1.15.0, 15 October 2026.

The edition number identifies the supplied source and text. A machine-readable citation is supplied in [CITATION.bib](CITATION.bib). See [REUSE.md](REUSE.md) for the current reuse status; this edition does not add a license grant.
