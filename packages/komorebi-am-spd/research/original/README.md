# Adaptive Multiscale Singular Packet Decomposition

## Final theory and verification edition

**Author:** Komorebi P.

This release is the completed finite formulation of AM-SPD.

The method combines:

- a moving geometry-aware packet atlas
- localized row, column, and channel singular models
- variable local rank
- an exact integer-budget Pareto tree
- a three-seed backward-replacement portfolio
- one global least-squares refit for every completed span
- an exact residual archive

The finite approximation is

\[
\widehat F
=
P_KA_K
+
\sum_{\nu\in\mathcal T}
M_{\Omega_\nu}
\left(U_\nu\Sigma_\nu V_\nu^{\mathsf T}\right).
\]

The complete finite reconstruction is always

\[
F=\widehat F+R_{\mathrm{archive}}.
\]

## Main results

The final bounded RMSE values are:

| Image | Final AM-SPD |
|---|---:|
| Synthetic geometry | 0.003155 |
| Synthetic text and curves | 0.003141 |
| Camera | 0.005064 |
| Astronaut | 0.010691 |

The bounded reductions from the original SPD results are about 15.3%, 7.5%, 66.1%, and 67.6%.

The ten-case structural suite shows a wider boundary. Full AM-SPD matches or improves on both restricted packet trees in all ten cases and beats the parameter-matched global SVD in seven.

The noise suite is intentionally reported without a favorable reinterpretation. Only nine of thirty-six noisy scenarios improve on the noisy input under the fixed-budget rule. AM-SPD is a representation method. A denoising version needs a noise model or risk-calibrated penalty.

## Proofs included

The paper proves:

- local fixed-rank SVD optimality for each declared unfolding
- the exact integer-budget tree recursion
- budget monotonicity
- global-refit dominance
- exact post-projection block gain
- finite-portfolio nonregression
- a singular-gap stability bound
- exact residual-archive reconstruction
- exact finite-raster closure

## Verification

Fresh verification completed successfully:

- 16 core packet-atlas groups
- 8 Singular Packet Decomposition groups
- 15 intermediate AM-SPD groups
- 11 final proof-oriented groups
- 12,154 final property scenarios with zero failures
- 9,960 exact dynamic-programming comparisons against exhaustive enumeration
- 10 structural stress cases
- 36 noise scenarios
- 147 rendered PDF pages
- 92 vector figures and 92 matching PNG figures

The final PDF has no preflight warnings, layout warnings, undefined references, clipped text, blank pages, one-line pages, visible semicolons, or bibliography.

## Reproduction

From the source directory:

```bash
python infinite_packet_gibbs_reconstruction.py --tests-only
python verify_singular_packet_decomposition.py
python verify_am_spd.py
python adaptive_multiscale_spd_final.py --base .
python aggregate_am_spd_final_results.py
python am_spd_final_stress.py --base . --size 32 --budget 720
python am_spd_noise_stress_small.py
python verify_am_spd_final.py
python generate_am_spd_final_tables.py
python generate_am_spd_final_figures.py
pdflatex -interaction=nonstopmode -halt-on-error Projector_Resolved_Adaptive_Multiscale_Singular_Packet_Decomposition_Final.tex
pdflatex -interaction=nonstopmode -halt-on-error Projector_Resolved_Adaptive_Multiscale_Singular_Packet_Decomposition_Final.tex
pdflatex -interaction=nonstopmode -halt-on-error Projector_Resolved_Adaptive_Multiscale_Singular_Packet_Decomposition_Final.tex
```
