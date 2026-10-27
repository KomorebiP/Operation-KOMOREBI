# Paper VI — complete source and visual-reader bundle

**Komorebi P.**  
**Formal baseline:** v0.5.0, Checked Fifth Block  
**Editorial layer:** 28-page worked visual appendix, September 12, 2026

## Read

`reading/Paper_VI_With_Visual_Appendix.pdf` contains the unchanged 34-page reviewed manuscript followed by the 28-page appendix (62 pages total). `reading/Paper_VI_Visual_Appendix.pdf` is the standalone reader guide. All appendix plates are editable vector TikZ, generated from explicit models. The original manuscript's graphics are retained, not redrawn or replaced.

The appendix distinguishes full coordinates, probability aggregation, conditional expectation, Bayesian normalization, spectral functional calculus, and hidden-state elimination. Worked cases include an exact four-state chain, loss of Bayesian sufficiency, a complete two-observation filter, a Dirichlet Green inverse, all eight three-step Feynman–Kac paths, Jordan memory, and phase-type survival.

## Preserve the original release

`original_snapshot/` contains all 534 original files, including the reviewed and earlier manuscript, Python companion, original figure generator, theorem ledger, Lean sources, dependency pins, licenses, provenance, and saved formal evidence. There are 47 current production proof modules; historical/provenance Lean sources are also retained and must not be counted as additional current modules.

The formal release records 33/33 scoped results complete and keeps three original conjectures separate. This editorial addition does not change any theorem, proof source, or hypothesis. No Lean executable was run for it. Do not interpret the appendix examples as new Lean-certified results.

## Verify the distributed files

From the extracted bundle root, in PowerShell, a terminal, or a Python-enabled shell:

```text
python Run-PaperVI.py verify
```

This uses only Python's standard library and checks every entry in `FILE_MANIFEST.json`, then checks the complete original snapshot. The manifest excludes itself by design. It does not certify mathematics or reject unrelated extra files you create after extraction.

## Reproduce the examples and reading editions

Install the stated Python dependencies in an isolated environment. A TeX installation with `pdflatex`, Latin Modern, TikZ, tcolorbox, hyperref/bookmark, and the packages listed in `visual_appendix/appendix.tex` is needed for typesetting. Installing dependencies can require a network; the supplied build scripts themselves perform no downloads.

```text
python Run-PaperVI.py examples --output-dir rebuilt/examples
python Run-PaperVI.py build --output-dir rebuilt/reading
python Run-PaperVI.py original-checks --output-dir rebuilt/original
```

`examples` reruns the 204 exact/symbolic checks and 11 rejected false controls in a temporary tree. `build` also regenerates the 26 vector plates, compiles the 28-page appendix, attaches the original PDF, adds source links, and checks all pages. `original-checks` reruns the original 54 Python tests, regenerates the 19 original figure pairs, compares numerical records, and rebuilds the reviewed LaTeX in an isolated temporary copy. These commands preserve the distributed sources and evidence.

The original replay compared 79 numerical metrics and matched the saved numerical records exactly. Numerical tests and sampled curves are distinct from the appendix's exact rational/symbolic checks. Version changes can alter floating-point roundoff, font rendering, or TeX output; a failure should be diagnosed, not silently relabeled as success.

## Replaying Lean is a separate task

The original full gate is documented in `original_snapshot/README.md` and implemented in `original_snapshot/verification/verify.py`. The exact toolchain and Mathlib pins are in `original_snapshot/formalization/lean/lean-toolchain` and `lake-manifest.json`. Run the original gate only in a working copy with those dependencies installed. The compiler and cache are not bundled. The reader-bundle launcher never invokes Lean.

## Where to edit

- Appendix text and math: `visual_appendix/source/pages.tex`.
- Mathematical model definitions: `visual_appendix/source/models.py`.
- Vector plates: generator `visual_appendix/source/generate_graphics.py`; generated editable plates in `visual_appendix/graphics/`.
- Independent calculations: `visual_appendix/checks/verify_examples.py`.
- Manuscript source: `original_snapshot/manuscript/Paper_VI_Reviewed.tex`; make a working copy before editing.
- Complete current and historical proof sources: `original_snapshot/formalization/` and `original_snapshot/provenance/`.

Changing a generated plate directly will intentionally fail the regenerated-plate parity check. Edit its generator for a reproducible change. Adjusting the text or calculations creates a new editorial version; it does not change the inherited formal release.

## Evidence

`verification/` separates source provenance, the current original Python/TeX replay, the appendix build, visual review, and development corrections. Recorded failures are retained and excluded from the final passing checks. The original saved Lean evidence stays inside `original_snapshot/`.

This is a complete source-and-evidence package, not a software installation. No Lean compiler, Mathlib cache, TeX distribution, installed dependencies, or font files are distributed.
