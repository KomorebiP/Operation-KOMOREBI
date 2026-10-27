# Paper XII — standalone visual guide

**Komorebi P. · Finalized 2026-10-06**

`Paper_XII_Visual_Guide_Final.pdf` is a standalone, source-aware worked guide to *Patching Support, Hecke Packets, and Conditional Automorphic Completion*. The first 18 topics preserve the existing worked appendix's substantive examples; the additional topics deepen actual completions, adequacy, augmentation, finite forests, matrix frames, polynomial effectivity, finite trace separation and the exact claim boundary.

The source is `Paper_XII_Visual_Guide_Final.tex` with `source/pages.tex`. Every drawing uses exact TikZ. The generator `source/generate_graphics.py` regenerates 22 assets; two further diagrams are written directly in `source/pages.tex`. Editable `.tex` assets and separately reusable `.pdf` vector figures are included in `graphics/`. There are no AI-generated or raster figures. Supporting Markdown (`.md`) files are included.

`SOURCE_COVERAGE.md` and `checks/SOURCE_ANCHORS.json` map every one of the historical 49 internal revised claims to a reading entry and an exact source label/line. The inherited revised census is **49 complete / 0 partial / 0 unchecked**. The original-wording census remains **41 complete / 7 partial / 1 unchecked**, with eight inherited amendments. This guide adds no new Lean certificate. External arithmetic inputs remain separate from internal conditional deductions.

The final companions expose standing conventions about finite S, coherent Frobenius normalization, the local coefficient-test category in global base change, the Fitting boundary r>n, and both compared Frobenius polynomial identities in ordinary completion. Those editorial clarifications are distinguished from the historical eight-amendment record. They were not newly replayed in Lean.

## Build in a fresh directory

Requirements: Python 3.10+, SymPy, PyMuPDF, and a TeX installation with `pdflatex`, Latin Modern, TikZ, tcolorbox, fancyhdr, preview, hyperref and the other packages named in the source.

```bash
python build.py --output-dir /absolute/path/to/fresh-output
```

The build regenerates **all** figure sources and standalone vector figure PDFs inside the selected directory, copies the two manuscript source files there, compiles twice, runs the exact example checker and performs PDF preflight. The date, metadata and PDF trailer behavior are fixed. No original manuscript PDF, network service, raster asset or Lean toolchain is required.

```bash
python checks/verify_examples.py --output /absolute/path/to/EXACT_CHECKS.json
python source/generate_graphics.py --output-dir /absolute/path/to/graphics
```

The checker records **46 exact illustrative assertions**: the inherited 31 plus 15 further assertions. It covers exhaustive finite coefficient models, symbolic minors, explicit CRT/projector identities, modular matrices and uniform identities used by the examples. Finite horizons are explicitly bounded; all-level and infinite claims have arguments in the guide. Arithmetic existence, classicality and the inherited general Lean claims are outside this checker.

Tested here with Python 3.12.14, SymPy 1.14.0, PyMuPDF 1.26.6 and pdfTeX 1.40.25. The default runtime did not initially provide SymPy; the verification used an existing local SymPy dependency directory through `PYTHONPATH`. The guide does not bundle that environment-specific path into its build script. Install the declared requirements in your chosen environment.

`checks/BUILD_AUDIT.json` reports the final PDF bounds, page/topic alignment, zero raster images, and absence of overfull boxes or unresolved references. `checks/REBUILD_COMPARISON.json` records the isolated rebuild. `AUDIT.md` records mathematical self-review and complete-page visual inspection. The figures and tests explain the revised source contract; they do not certify universal companion existence or unrestricted reciprocity.

To compare two finished output directories, run `python checks/compare_builds.py first-output second-output --output comparison.json`. Add `--render-dir preview-pages` to render all pages at 140 dpi.
