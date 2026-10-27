# Realization Calculus | Special Functions

## Function Families and Their Structure
*Coupled growth, arithmetic depth, and finite resolution*  
Komorebi P.

The standalone publication is `Realization_Calculus_Special_Functions.pdf` at the root of this package. Its source is in `main.tex`, with `realization-design.tex` providing the modern Realization Calculus book design.

### Contents
The mathematical volume is organized into five parts:
1. Entire Functions and Their Growth
2. Arithmetic Depth and Signed Measures
3. Orbit Spectra and Exact Coordinates
4. Coupled Systems and Finite Resolution
5. Proofs, Evidence, and Sources

Part V contains complete technical derivations, the results and their evidence boundaries, a notation glossary, and literature comparisons.

### Build
From the directory, run:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

LaTeX requires TeX Live with the amsmath, mathpazo, titlesec, TikZ, fancyhdr, microtype, and hyperref packages. All in-manuscript mathematical diagrams are included as vector PDF sources under `figures/` and `figures_v11/`; external data downloads are not part of the PDF build.

### Computation checks and claim boundaries
Fresh execution of `checks/run_v11.py` from the source directory passed 5,272 exact assertions, 26 numerical assertions, 13 operational guards, and generated all 14 expected figure pairs. A new local summary is preserved in `verification/fresh_coupled_run.json`.

The 19,871 exact and 5,576 numerical checks for the preceding four families are inherited from the preserved source archive. The original four-family suite was not rerun as part of this layout revision. Neither suite is a formal Lean proof or an independent verification of all analytic arguments. Historical novelty of the candidate extensions remains bounded by the literature comparison, and the explicitly listed open problems remain open.

### Provenance
Original mathematical source, tests, figures, correspondence, and audit data remain in this directory. The earlier reader documentation is available as `PROVENANCE_ORIGINAL_README.md` and the rest of the historical records remain under their original paths. The reformatted manuscript does not claim additional theorems. It changes presentation and reader navigation and corrects a small number of textual references or redundant lines.

The older companion visual PDF `visual_guide.pdf` is included in its earlier design. It was not comprehensively re-typeset in this edition.

No new license is applied by the reformatting operation. Consult the source documents or arrange a license separately before redistribution.
