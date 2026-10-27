Paper V visual guide, monograph edition
20 October 2026

From this directory run:
  python3 build.py
  python3 build.py --check-only

The builder copies the full source tree into an isolated directory and runs
four XeLaTeX passes. TeX packages come from your TeX distribution. Required fonts are resolved with kpsewhich, copied only into temporary staging,
and recorded by SHA-256. No font binaries are distributed by this release.
See FONT_DEPENDENCIES.txt at the package root.
PDF assembly does not rerun mathematics or Lean.

Regenerate all 37 current figures from their current source models:
  python3 regenerate_monograph_figures.py
  python3 regenerate_monograph_figures.py --check-only
The generator requires SymPy, NumPy and Matplotlib. Core and extension plates
retain exact models; Fourier/trigonometric samples remain illustrations.

Fresh finite checks and rejected false controls are recorded in
checks/monograph_run/. Original reports remain separate historical evidence.
No fresh Lean compiler run is claimed. All 40 worked-page formulas and figure
identities are preserved, with one documented LaTeX grouping correction.

Render and structurally check all 43 PDF pages:
  python3 qa_pdf.py
Then inspect the qa/contact sheets and selected detail images.

refresh_monograph_locators.py changes only traditional statement locators
using the final traditional canonical map. It leaves formulas and figure
identities unchanged. See VISUAL_CROSSWALK.json and VERIFICATION.json.
