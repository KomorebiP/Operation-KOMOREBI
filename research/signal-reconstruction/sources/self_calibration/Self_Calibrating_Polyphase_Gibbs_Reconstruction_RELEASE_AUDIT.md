# Release Audit

## Document

- Title: **Self-Calibrating Polyphase Fourier Reconstruction**
- Author: **Komorebi P.**
- Pages: **68**
- Figure pairs: **40 vector PDFs + 40 PNGs**
- Single implementation: `polyphase_gibbs_breakthrough.py`
- Named computational checks: **31/31 passed**

## Theorem package

The release proves, under its declared finite-rate and regularity hypotheses:

1. exact offset-channel phase progression
2. multi-offset phase recovery and deterministic perturbation control
3. unknown-order recovery from an exact or separated Hankel rank
4. branch selection from a checkable geometric margin
5. one-order improvement when lifting decimated node errors
6. equality of the self-calibrated branch and the oracle branch under that margin
7. preservation of the decimated location rate
8. exact bandlimited recovery from an explicit high-frequency budget of `3*Lmax + 1` coefficients
9. perturbed recovery for non-bandlimited smooth backgrounds under uniform local inverse bounds
10. a resolved synthesis inequality with no persistent Gibbs edge term
11. a confluent extension for higher jump jets

The release does not claim separation-free recovery, arbitrary edge geometry, unbounded model order, a global minimax theorem, or confirmed historical priority for the complete package.

## Numerical record

- Oracle/self-calibrated maximum node-set distance over 28 tail/decimation combinations: `2.220446049250313e-16`
- Random separated unknown-order family: `100/100` order recoveries and `100/100` location recoveries below `1e-3`
- Random-family median location error: `1.1881870274343953e-06`
- Random-family maximum location error: `0.0002839821194893233`
- Exact 19-coefficient control location error: `9.769962616701378e-15`
- Exact 19-coefficient control jump error: `5.773159728050814e-15`
- Resolved reconstruction RMSE: `4.83744790320189e-07`
- Raw Fourier RMSE: `0.047716357033348394`
- Fejer RMSE: `0.06661000567562357`

## PDF and layout

- PDF preflight warnings: **0**
- Encryption: **none**
- Scanned/image-only pages: **none**
- Fonts not embedded: **0**
- Overfull boxes: **0**
- Underfull boxes: **0**
- Undefined references: **0**
- Blank pages: **0**
- One-line pages: **0**
- Minimum nonblank text lines on any page: **8**
- All pages rendered at 180 DPI and reviewed through the complete contact sheet

## Reproduction

The source release was designed to rebuild from one Python program and one LaTeX source. The provided PowerShell and shell runners regenerate the figures, tables, numerical ledger, and PDF. They do not reinstall packages automatically.
