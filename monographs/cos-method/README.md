# The K-COS Method

**Structured Gaussian Quadratic Forms, Spectral Compression, and Certified Extreme-Tail Evaluation**  
Komorebi P. · Realization Calculus

## Publication master

Open **K_COS_Monograph.pdf**. This is the closing publication master: 138 pages, four parts, twelve chapters, four appendices, seventeen numbered visual studies, and fifty vector graphics. It supersedes the previous monograph and figure editions. The source is the latest corrected vector-figure branch, not an earlier design branch.

The mathematical statement inventory remains 61 numbered environments and 39 proofs. The closing edits clarify assumptions, logarithm branches, pruning boundary cases, notation, and numerical guarantees. Four statement/proof environments were edited; their exact changes are recorded. Inventory preservation does not independently prove their validity.

| Path | Contents |
| --- | --- |
| `K_COS_Monograph.pdf` | Authoritative book with linked contents and bookmarks |
| `book/` | Editable LaTeX, typography, references, and figures |
| `book/figures_production/` | Fifty unchanged PDF/SVG/PNG figure sets |
| `illustrations/production_figures.py` | Publication-figure generator |
| `engine/` | Numerical engine, tests, and retained data |
| `lean/` | Pinned formal source and retained compiler evidence |
| `verification/closing/` | Current replay, finite controls, source diff, and publication audit |
| `verification/figure_pass/` | Earlier figure-production evidence, retained as provenance |
| `verification/current_revision/` | Earlier numerical records, retained as provenance |
| `provenance/` | Source archives and concordance |

## Verify the delivered package

```text
python verify_manifest.py
```

This standard-library command compares the supplied files with `SHA256SUMS.txt`. Run it before regeneration. Rebuilding or replaying may change files and invalidate the delivered byte manifest.

## Build the book

```text
python build.py
```

The builder runs pdfLaTeX three times and copies the book to the package root. Install a TeX distribution containing the packages named in `book/monograph.sty`. Supplied graphics are sufficient for typesetting; numerical calculations need not be rerun to build the PDF. Font binaries and TeX installations are not bundled.

## Reproduce numerical checks

```text
python -m pip install -r requirements-engine.txt
python replay.py --include-controls --output verification/local_replay
```

The closing replay in `verification/closing/numerical/` passed **60 of 60 tests** and both independent interval controls. It is a fresh execution, distinct from the older figure-pass records. The numerical source and retained data were unchanged.

For the worked example and finite algebra checks:

```text
python -m pip install -r requirements-illustrations.txt
python illustrations/worked_example.py
python verification/closing/finite/exact_algebra.py
python verification/check_range_core.py
python verification/closing/finite/closing_controls.py
```

Work in a copy. The original worked-example driver writes its declared results and auxiliary figures under `verification/current_revision/` and `book/figures_edition/`; those are not the authoritative publication figures. The closing replay was isolated so that historical records and final graphics were not overwritten.

## Publication audit and page rendering

```text
python -m pip install -r requirements-publication.txt
python audit.py
python verification/closing/render_review.py --output /tmp/kcos-page-review
```

The audit checks the source inventory and explicit changes, figure/data correspondence, recorded execution results, page geometry, navigation, and final build diagnostics. It reads the numerical records; it does not rerun the numerical tests or prove the theorems. Rendering produces all pages and contact sheets for visual review.

## Regenerate the fifty publication figures

```text
python -m pip install -r requirements-illustrations.txt
python illustrations/production_figures.py
python build.py
```

The older `generate_figures.py` and `redraw_recorded_figures.py` are provenance, not the generator for the final vector assets. Source fonts are referenced by name; exact text metrics can depend on the installed font versions. The delivered PDF/SVG/PNG assets are the publication master.

## Verification scope and rights

Read `VERIFICATION_REPORT.md` for the closing checks and limits. Lean was **not recompiled** because neither `lean` nor `lake` was available in the closing environment. The formal source, dependency pins, and historical compiler records remain unchanged. The limited formal companion does not establish end-to-end correctness of the probability analysis or arithmetic implementation.

No new hardware benchmark, universal performance claim, or broader directed-rounding guarantee is introduced. Source-specific notices and external dependency terms remain in force. Assembly does not infer a new license. No font binaries are supplied.
