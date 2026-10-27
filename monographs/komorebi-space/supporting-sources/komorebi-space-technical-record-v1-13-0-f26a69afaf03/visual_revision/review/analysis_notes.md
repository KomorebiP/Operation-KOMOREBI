# Analytic visual investigations

Eight new compositions replace single-instance theorem illustrations with parameter sweeps, comparisons, and worked predictions. The source is `tools/visual_companion/analysis.py`; scene prose and monograph section labels are generated into `records/analysis_scenes.json`.

## Mathematical scope

- All finite geometry uses Euclidean norms, except the movement investigation, which explicitly uses the complete finite-dimensional `l1` metric.
- The protected-angle scene changes the protected observable with the direction; it does not claim one observable is preserved across different experiments.
- The kernel-motion formulas use positive scale and angles between zero and pi/2; the plot begins at five degrees to avoid the logarithm of a zero operator difference.
- The datum-exponent scene evaluates finite prefix energies through 4096 equations. Its infinite conclusion follows from the displayed preimage and the square-series test, not from the plotted sample. These new worked values are not claimed to be dedicated Lean instances.
- The budget profile is parametrized by exact regularized corrections at their own budgets. The uncertainty band is centered on the height-one-half profile and allows data error 0.03 plus operator error 0.05 times the budget, on a fixed correction space.
- The two-mode noisy calculation has a known exact answer and deterministic noise, so it plots actual errors, not statistical confidence or universal optimal parameter claims.
- The near-dependent basis remains a full basis only at positive parameter. Its endpoint is explicitly excluded from the full-space certificate.
- The stopping phase map records sufficient guaranteed exponents for the attainable diagonal datum, retaining the rounded integer parameter. Uncolored regions mean this bound does not vanish, not that all numerical answers fail to converge.

## Verification and visual review

The computation-audit skill guided the distinction between mathematical statements and finite checks. The generated check report records Python, NumPy and Matplotlib versions, the exact generation command, numerical tolerance, arithmetic domains, finite inputs, checks, and PDF SHA256 values. Geometry checks use direct matrix formulas. The basis metric is also checked with exact rational arithmetic. No randomized checks or uncontrolled infinite truncations are used.

All eight PNG previews were inspected at native output size. The first render exposed a crowded boundary between the three-dimensional budget chart and the neighboring residual chart, and an overlong title in the basis chart. The budget axes were separated and made slightly narrower; the basis titles were shortened and aligned. The final stopping heatmap retains vector geometry with a smaller deterministic grid to reduce PDF size without changing the formulas or its interpretation. A Python string warning was also removed. All visible figure text is checked to be at least 10 points. Figure size is seven by 4.8 inches throughout.

The independent read-only reviewer verified the eight models, worked predictions, domains, and monograph pointers against the source. A separate review output belongs to that reviewer. The root assembler remains responsible for checking the figures and text once placed in the final PDF.

## PDF-backend seam correction

Inspection of the assembled guide exposed white antialiasing seams between vector heatmap cells in a02 and a08 that were absent from the Matplotlib PNG previews. A 0.1-point same-color edge overlap was tested but still left visible crosshatching in Poppler. The final fix gives each QuadMesh cell a 0.6-point face-colored edge and disables mesh antialiasing. The mesh remains vector geometry; the data grids, formulas, captions, axes, and all other scenes are unchanged.

Both final figure PDFs were rendered independently with `pdftoppm -png -singlefile -r 160` and inspected. The resulting a02 and a08 images have smooth fills without the white grid artifacts. The PDF-derived review images are temporary files under `/tmp/komorebi_analytic_pdf_review/`. Regeneration still passes all 44 analytic checks and updates the PDF hashes in `build/analysis_checks.json`. This fixes the vector PDF backend rather than relying on a clean source PNG.
