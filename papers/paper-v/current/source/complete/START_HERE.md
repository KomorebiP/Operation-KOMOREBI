# Paper V — complete source bundle with visual appendix

**Author:** Komorebi P.  
**Preserved formal edition:** v1.1.0 Expanded Lean Checked  
**Editorial addition:** 26-page worked visual appendix, September 12, 2026

## Read

- `reading/Paper_V_With_Visual_Appendix.pdf`: 65 pages. The original 39 pages are unchanged; the new 26 pages follow them.
- `reading/Paper_V_Visual_Appendix.pdf`: standalone appendix with page bookmarks.
- `reading/Paper_V_Original_v1.1.0.pdf`: the untouched original manuscript.

In the combined edition, each gray source line below an appendix title is a link to the relevant original passage. The PDF outline provides one entry per appendix page.

## Find the editable materials

| Directory | Contents |
|---|---|
| `original_snapshot/` | All 424 original release files, preserved byte-for-byte. |
| `original_snapshot/manuscript/` | Current original TeX, PDF, and 18 figure pairs. |
| `original_snapshot/companion/` | Original Python package, tests, figure generator, numerical records, and requirements. |
| `original_snapshot/formalization/lean/` | Original Lean project, dependency pins, and proof sources. See the original source index if locating a particular module. |
| `original_snapshot/provenance/` | Earlier manuscript records and source provenance, not the current editorial layer. |
| `visual_appendix/` | Editable LaTeX, 24 generated TikZ plates, exact SymPy models, exact tests, and an isolated build script. |
| `verification/` | Fresh editorial and Python replay records, preservation inventories, and development corrections. These do not claim a fresh Lean run. |
| `tools/` | The isolated original-source audit runner. |

## Quick verification

From the extracted bundle root:

```powershell
python Run-PaperV.py verify
```

This checks the distributed SHA-256 manifest and the independently retained original-file inventory. Only Python's standard library is needed. Extra output files are not evidence covered by this manifest.

To rerun the new exact examples:

```powershell
python Run-PaperV.py examples
```

To rebuild the appendix and combined PDF:

```powershell
python Run-PaperV.py build
```

To replay the original Python tests, numerical records, original figures, and manuscript build:

```powershell
python Run-PaperV.py original-checks
```

Use `--output-dir PATH` to choose a separate output directory. These commands operate in temporary working copies and keep the original source and shipped evidence untouched. Generated output goes to `rebuilt/` by default. None of these root-runner commands invokes Lean.

## Dependencies and tested environment

The new examples need Python 3.10+ and SymPy. PDF assembly needs PyMuPDF and pypdf. The TeX build needs `pdflatex`, Latin Modern, amsmath/amssymb/mathtools, microtype, graphicx, geometry, array/booktabs/tabularx/multicol, TikZ/PGF, tcolorbox, fancyhdr, xcolor, hyperref, and bookmark. Original numerical tests additionally use their own companion requirements. See `visual_appendix/requirements.txt` and `verification/ENVIRONMENT.json`.

The compiler, Mathlib cache, TeX distribution, font installation, and installed Python dependencies are **not bundled**. No network connection is needed by the supplied scripts once those prerequisites are installed. Native Windows execution was not tested; Python/TeX commands should be run in a compatible local environment, with Linux/WSL suitable for the inherited Lean tooling.

## Formal scope and evidence boundary

The original release records twenty scoped theorem-like statements, 225 supporting theorem targets, and 23 proof modules. Its original formal records and two open edge-recovery problems are preserved. This editorial task did **not** run Lean, alter a theorem, promote an open claim, or count explanatory examples as new formal proofs.

Fresh work here consists of:

- 181 exact arithmetic, symbolic, matrix, and exhaustive finite checks, plus seven deliberately false controls;
- all 69 original Python tests;
- original regeneration of 18 figure pairs and exact comparison of the saved numerical records;
- original 39-page TeX rebuild and text/render comparison;
- appendix generation, 26-page TeX build, source-link insertion, and preservation of all 65 input PDF pages;
- archive integrity and an additional appendix rebuild from an extracted delivery ZIP.

The appendix's continuous Fourier and sensitivity curves are numerical samples of displayed formulas, not certified root enclosures or numerical proofs of universal approximation rates. Rational sample labels, matrices, exact finite enumeration, and symbolic formulas have separate exact checks.

## Replaying Lean separately

Read `original_snapshot/README.md`, `original_snapshot/MANUSCRIPT_TARGET_MAP.md`, and the original verification instructions. The pinned Lean toolchain is `leanprover/lean4:v4.34.0-rc2`; Mathlib is pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Use a separate copy before invoking original combined verifiers, which may write fresh logs and require additional tooling. Passing `Run-PaperV.py verify` is never a replacement for that kernel build.
