# v0.5 verification

## Analytic scope

The manuscript proves:

- weighted phase-transfer envelope;
- thresholded-power certificate;
- certified approximate light cone;
- scalar depth-threshold law;
- finite Krylov-polynomial certificate;
- certified pruning corollary.

## Automated tests

- `test_streaming_skat.py`: 6/6 PASS.
- `test_formal_v02.py`: PASS.
- `test_approximate_lightcone.py`: 5/5 PASS.

## Deterministic computation

- phases: 12;
- phase width: 4;
- operator dimension: 48;
- start block width: 3;
- seed: 20260923;
- arithmetic: float64;
- depths: 1 through 8;
- pruning thresholds: 7;
- polynomial degree: 4.

All observed phase envelopes, thresholding-error bounds, threshold-sweep
certificates, and polynomial certificates passed.

Maximum observed ratios:

- actual outside-cone leakage / certified outside-cone bound: 0.6694;
- actual threshold-sweep error / certified bound: 0.3763;
- phasewise polynomial error / certificate: 0.0679.

## PDF verification

- pages: 24;
- rendered with the PDF skill at 160 dpi;
- new theorem pages and figures visually inspected;
- no overfull boxes, undefined references, or broken glyphs;
- two harmless underfull-box warnings remain in an existing prose/table region.

## Claim boundary

The analytic approximation errors are proved. The finite experiment is not a
proof and does not determine hardware-optimal thresholds. The phase-transfer
certificate can be conservative because it discards cancellation and alignment.
