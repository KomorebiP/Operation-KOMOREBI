# Komorebi Quadratic-Form Engine v1.9 verification

Date: 2026-09-24

## New verified-spectrum layer

`test_verified_spectrum.py`: **4/4 PASS**.

The tests cover:
- exact-binary known-spectrum containment;
- outward-endpoint serialization (regression for the draft endpoint-collapse bug);
- random dense binary64 factor containment against independently recomputed high-precision eigenvalues;
- end-to-end binary64 matrix-to-tail certification near p=1e-16.

The frozen v1.8 production regression baseline remains **41/41 PASS**. A later attempt to rerun the entire historical suite in one process exceeded the execution window, so v1.9 does not mislabel that attempt as a fresh combined 45/45 run.

## Random dense spectral controls

Factors 12x18, 20x30, and 28x36 contained every independently recomputed high-precision eigenvalue of the exact dyadic Gram matrix. Maximum relative spectral interval width across the three cases was approximately 1.20e-56.

## End-to-end matrix-defined tail

Dense binary64 64x64 factor, q=131.33201485100517:
- requested 1e-10 relative probability accuracy: certified, achieved about 2.60e-12;
- requested 1e-12: certified, achieved about 4.09e-15.

The eigensolver is outside the trust base: candidate Q,D are accepted only after directed-rounding orthogonality and reconstruction postchecks.

## Current boundary

The verified spectral theorem is general, but the current implementation forms a full dense candidate basis. The next rigor/scalability step is a verified streamed range-core and residual-completion implementation for very large factors.

## PDF

The final manuscript is 67 pages, opens cleanly, is unencrypted and text-based, and passes PDF preflight. The new theorem/result pages and the corrected scope table were rendered and visually inspected.
