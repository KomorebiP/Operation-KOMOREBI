# Komorebi Quadratic-Form Engine manuscript v1.7 verification

Date: 2026-09-24

## New independent inversion battery

Four heterogeneous central-positive generalized chi-square spectra were evaluated near log10 p = -16 using the production K-COS solver and an independent high-precision direct characteristic-function inversion.

Absolute K-COS minus inversion discrepancies in log10 probability:

- balanced rank 80: 6.52e-15 decades;
- skewed rank 80: 4.13e-15 decades;
- spiky rank 80: 5.19e-15 decades;
- balanced rank 120: 2.88e-15 decades.

Implied relative probability differences range from approximately 6.64e-15 to 1.50e-14.

Each inversion reference was evaluated at two truncation limits. The final omitted-integral bound relative to p ranges from 4.19e-29 to 7.00e-17, and the observed change between truncations is smaller than the K-COS/reference difference in all four cases.

## PDF verification

- LaTeX compiled successfully through three passes.
- PDF preflight: openable, unencrypted, 64 pages, not scanned.
- 64 pages rendered successfully at 120 dpi.
- New inversion subsection and figure were visually inspected on pages 12-13.
- Render comparison against v1.6 completed at 72 dpi; differences are consistent with the inserted section and page-flow shift.

## Evidence boundary

The inversion battery is independent numerical validation, not a replacement for the rigorous directed-rounding enclosure. The strongest positive exact-spectrum guarantee remains the accuracy-driven interval backend. The new battery specifically supports the claim that the fast point evaluator remains accurate near p=1e-16 on heterogeneous spectra.
