# The K-COS Method

**Structured Gaussian Quadratic Forms, Spectral Compression, and Certified Extreme-Tail Evaluation**  
Komorebi P. · Realization Calculus

Open **K_COS_Monograph.pdf** for the 141-page book. This package preserves the corrected mathematical source and replaces the complete figure set with a consistent vector system. It contains four parts, twelve chapters, seventeen visual studies, formal correspondence, computational reproduction, a glossary, and consolidated references.

## Figures

All 49 baseline graphics were rebuilt and one directed-refinement graphic was added. The **50 PDF/SVG/PNG sets** are in `book/figures_production/`. The SVGs retain editable text. The PDF graphics are the assets used by LaTeX. PNGs are previews only. Labels distinguish recorded experiments, sizing or execution models, and declared examples. No new hardware benchmark is claimed.

| Path | Role |
| --- | --- |
| `K_COS_Monograph.pdf` | Complete linked book |
| `book/` | Editable LaTeX, typography and references |
| `book/figures_production/` | Authoritative vector figures and previews |
| `illustrations/production_figures.py` | Regenerate all 50 publication graphics |
| `illustrations/figure_style.py` | Shared typography, palette, geometry and bounds checks |
| `illustrations/publication_data/` | Restored packet tables and explicit rounded summaries |
| `engine/` | Unchanged corrected numerical engine, tests and data |
| `lean/` | Unchanged formal source and retained compiler evidence |
| `verification/figure_pass/` | Current figure manifest, audits, source diff and visual review |
| `verification/current_revision/` | Retained earlier numerical replay, not a new run |
| `provenance/` | Original archives, concordance and earlier reports |

## Build the supplied book

```text
python build.py
```

The builder uses pdfLaTeX for three passes and copies the resulting PDF to the package root. A TeX installation with the packages in `book/monograph.sty` is required. The supplied vector assets are sufficient to typeset the book without running numerical examples.

## Regenerate the graphics

```text
python -m pip install -r requirements-illustrations.txt
python illustrations/production_figures.py
python build.py
```

No engine benchmark or Lean compilation is performed by the figure generator. It reads preserved data and recomputes its declared illustrative models. The output manifest records source hashes, evidence scope, and finite checks. Regenerate in a copy because this changes the delivered checksums.

The older `generate_figures.py` and `redraw_recorded_figures.py` are retained for provenance. They are **not** the generator for the current publication assets.

## Audit and numerical replay

```text
python verification/figure_pass/audit_publication.py
python verify_manifest.py
```

The publication audit additionally needs PyMuPDF. It checks source preservation, figure files and hashes, page geometry, labels, and navigation. It does not certify theorem validity or interval-library correctness.

To execute the separate numerical tests and controls:

```text
python -m pip install -r requirements-engine.txt
python replay.py --include-controls
```

The earlier technical replay passed 60 tests and the independent controls. **That replay was not repeated for this figure edition.** The engine and data files match the baseline byte-for-byte. Lean was not recompiled, and its retained compiler records are historical evidence.

## Scope and rights

Read `VERIFICATION_REPORT.md` for the actual checks, recovered production issues, and limits. No mathematical claim was promoted by changing its illustration. All 61 theorem-family environments and 39 proof environments remain unchanged. Source-specific notices and external dependency terms remain in force. No new license is inferred by assembly. No font binaries are included.
