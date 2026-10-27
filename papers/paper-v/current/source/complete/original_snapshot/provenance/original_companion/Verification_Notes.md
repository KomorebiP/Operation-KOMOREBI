# Verification Notes

## Release identity

- Paper: **Projector-Resolved Seed Calculus V: Polyphase Signal Calculus: Exact Reconstruction, Edge Packets, Wavelets, and Smith Coordinates**
- Author metadata: **Komorebi P.**
- Build date: 2026-07-28
- Final PDF length: **31 pages**

## Mathematical and numerical checks

- Automated tests: **33/33 passed**
- Polyphase analysis-synthesis residual: `0`
- Nested-refinement residual: `0`
- FIR polyphase transfer residual: `4.440892098500626e-16`
- Haar reconstruction residual: `8.881784197001252e-16`
- Haar energy residual: `5.684341886080802e-14`
- Wavelet-packet reconstruction residual: `2.220446049250313e-15`
- Wavelet-packet energy residual: `2.2737367544323206e-13`
- Predict-update lifting residual: `4.440892098500626e-16`
- Nonlinear product-packet residual: `1.3322676295501878e-15`
- Smith round-trip residual: `8.881784197001252e-16`
- Smith phase-rotation residual: `3.342213888644167e-16`
- Smith two-phase inversion residual: `5.551115123125783e-16`
- Smith impedance-admittance duality residual: `0`
- Smith circle-equation residual: `1.0658141036401503e-14`

The floating-point residuals are finite implementation checks. They are not substitutes for the symbolic proofs in the paper.

## Adaptive packet-tree certificate

- admissible depth-five prunings: `458330`;
- dynamic-programming versus exhaustive-search cost residual: `0`;
- selected mixed-depth packets: `000, 001, 0100, 0101, 011, 1`;
- exact mixed-depth synthesis residual: `8.881784197001252e-16`;
- unique optimum gap: `0.00031908894232213214`;
- twice the declared perturbation envelope: `0.000064`;
- stability certificate: `true`.

## Edge-study record

### One-dimensional example

- global Fourier RMSE: `0.05402293652087033`
- exact known-packet RMSE: `0.00013691775180553568`
- limited estimated-packet RMSE: `0.024028509481815737`
- estimated mask IoU in this synthetic case: `1.0`

### Two-dimensional disk example

- global Fourier RMSE: `0.037643280877381294`
- exact known-packet RMSE: `6.475173886803166e-05`
- limited estimated-packet RMSE: `0.0034042967376725327`
- global boundary-band RMSE: `0.1854132664803113`
- exact known-packet boundary-band RMSE: `1.2709460721840048e-05`
- limited estimated-packet boundary-band RMSE: `0.008883387549767098`

### Multiple-edge stress example

- global Fourier RMSE: `0.03374045049665539`
- exact known-packet RMSE: `5.211836105818543e-07`
- global maximum error: `0.32807382546218977`
- exact known-packet maximum error: `9.709945719180157e-06`

The known-packet studies test the conditional theorem in which the discontinuous component is supplied exactly. They do not establish automatic recovery of that packet from arbitrary data.

## Generated material

- Figure pairs: **18 PNG + 18 vector PDF**
- Numerical summary tables: **3 CSV files**
- Machine-readable result files: **2 JSON files**
- Installable wheel: `projector_seed_signal-1.1.0-py3-none-any.whl`
- Clean wheel installation and import: verified

## LaTeX and page audit

- `latexmk` completed successfully.
- Undefined references or citations: **0**
- Overfull boxes: **0**
- Underfull boxes: **0**
- Paper-local citation commands, bibliography items, or bibliography environments: **0**
- All 31 pages rendered successfully.
- `Verification_Render.png` contains a complete contact sheet.
- Pages containing the title, edge theorems, two-dimensional figures, Smith chart, numerical tables, and final appendices were inspected at full size.
- No clipped text, overlapping panels, broken glyphs, or missing figures were observed.

## Metadata and privacy audit

Visible PDF metadata is limited to:

```text
Title: Projector-Resolved Seed Calculus V
Author: Komorebi P.
Subject: Polyphase signal calculus, edge packets, wavelets, and Smith coordinates
```

Creator, producer, creation-date, modification-date, and XMP fields are absent. The source and release files were scanned for personal names, private working paths, conversational remnants, and model-production language.

## Computational environment

The study is CPU-based and requires Python 3.10 or later with NumPy, SciPy, Matplotlib, and pytest. No GPU result is claimed.

## Claim boundary

The release proves the finite and functional statements under the hypotheses written in the paper. It does not establish:

- universal or stable discovery of discontinuity packets from arbitrary noisy data;
- universal removal of Gibbs phenomena without correct packet separation;
- superiority of wavelet packets for every sparsity budget or signal class;
- optimality of the proposed Smith boundary-weighting rule;
- minimax or infinite-tree statistical guarantees for adaptive selection.

The finite adaptive packet-tree problem is proved.  Broad stable edge-packet recovery and asymptotic adaptive-selection theory remain open.

## Archive validation

The final release workflow verifies:

- complete release extraction;
- complete release checksum verification;
- complete release test-suite execution;
- source-focused archive extraction;
- source-focused test-suite execution;
- source-focused reconstruction of the 31-page PDF;
- wheel installation into a clean target and import of `projector_signal`.
