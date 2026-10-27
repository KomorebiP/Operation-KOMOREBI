# Budget figure legend correction

Corrected only the plotted legend of plate `32_budget_certificate.pdf`, shown as Figure 28 on physical page 109 in the reviewed draft. The ellipse represents reachable images `T(B_M)` in residual-coordinate space, not the translated fit-residual set `r-T(B_M)`.

Exact plotted-text change:

- Before: `Reachable residuals at the fixed budget`
- After: `Reachable images at the fixed budget`

## Source and artifact identity

Inherited plotting source: `work/Komorebi_Space_Monograph_v1.7.0/checks/build_regularization_figures.py`.

Inherited source SHA256: `6b32b6d7ee5033fc034e0ba129b5d090cd424e681f4275bf580d33d40d6e0da6`.

New isolated builder: `monograph_v1.9.0/scripts/build_budget_figure.py`.

New builder SHA256: `5a523904f0feb09961655f87c8716cedcdfee71d575d070f2b0cfcf2fccaa237`.

Previous figure PDF SHA256: `c3a2d4fa6d5ee27af2b55dfeb7854b96a33ba923d14572b56ff6f9153b8f3744`.

Corrected figure PDF SHA256: `9f2b904305db55d33b8c847f492d83115272a5e00c50a0ae15cfcbdcf4864e9b`.

The builder writes only `source/figures/32_budget_certificate.pdf`. It does not rewrite the TeX inclusion, rerun the other five regularization figures, import the certificate program, or regenerate any mathematical evidence. The volatile PDF creation/modification date metadata is omitted for reproducibility.

## Preserved parameters and geometry

The complete original figure-32 plotting block was compared literally with the extracted block after replacing only the legend string. This comparison passed. In particular, all of the following remain unchanged:

- `T=diag(1,1/2)`, `r=(1,1)`, `a=(1/2,2/5)`.
- `M=sqrt(41)/10`, ellipse semiaxes `M` and `M/2`, centered at zero.
- `Ta=(1/2,1/5)`, `v=r-Ta=(1/2,4/5)`.
- The 600-point angular sampling and 100-point supporting-line sampling.
- Supporting-line tangent direction `(0.8,-0.5)` and parameter interval `[-0.63,0.65]`.
- Arrow from `Ta` to `r`, all three point locations, annotations, and callout placement.
- Figure dimensions `(7.5,4.0)` inches, equal aspect ratio, limits `(-0.85,1.62)` and `(-0.66,1.3)`, and both residual-coordinate axis labels.
- Font family/math font, font sizes, PDF font embedding setting, line widths, fill opacity, marker sizes, colors, and save padding.

## Build and direct visual inspection

Command: `python monograph_v1.9.0/scripts/build_budget_figure.py`.

First build terminal exit: **0**. A second identical build also returned **0** and produced the same corrected PDF SHA256 above. No build failure occurred.

The old and new PDFs were separately rendered with `pdftoppm -png -r 144 -singlefile`. Both actual rendered figures were opened with `view_image` at original detail. The corrected legend remains readable and clear of the point/annotation at `r`; all axes, point labels, arrowheads, ellipse geometry, and the supporting line remain legible. No clipping or overlap was found.

Both renders are 696 by 544 pixels. Their changed-pixel bounding box is `(281,35,508,54)`, confined to the first legend text line. All pixels outside that box are identical. Temporary comparison renders are in `tmp/budget_figure_review/` and are not additional publication artifacts.

The root publication build must still render the corrected plate within the final monograph after layout changes. This correction adds no theorem or Lean verification claim.
