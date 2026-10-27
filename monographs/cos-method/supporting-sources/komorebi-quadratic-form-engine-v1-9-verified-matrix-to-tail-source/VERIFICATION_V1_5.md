# Komorebi Quadratic-Form Engine v1.5 verification

## Accuracy-driven exact-spectrum controls

 target_log10_p  requested_relative_accuracy  certified  achieved_ratio_minus_one  width_decades   K  L  interval_dps  refinements  runtime_seconds
           -100                 1.000000e-08       True              2.450463e-10   1.064223e-10  64 10            50            3         1.166374
           -100                 1.000000e-10       True              2.057112e-12   8.933926e-13 128 10            50            4         1.552290
           -100                 1.000000e-12       True              9.293279e-17   4.036020e-17 128 12            50            5         1.928557
           -100                 1.000000e-14       True              9.293279e-17   4.036020e-17 128 12            50            5         1.927965
          -1000                 1.000000e-08       True              2.583693e-10   1.122084e-10  64 10            50            3         1.123976
          -1000                 1.000000e-10       True              1.615074e-11   7.014177e-12 128 10            50            4         1.467155
          -1000                 1.000000e-12       True              7.293412e-16   3.167489e-16 128 12            50            5         1.909593
          -1000                 1.000000e-14       True              7.293412e-16   3.167489e-16 128 12            50            5         1.957032
          -5000                 1.000000e-08       True              3.191027e-10   1.385845e-10  64 10            50            3         1.079640
          -5000                 1.000000e-10       True              7.696330e-11   3.342474e-11 128 10            50            4         1.449381
          -5000                 1.000000e-12       True              3.475380e-15   1.509338e-15 128 12            50            5         1.836444
          -5000                 1.000000e-14       True              3.475380e-15   1.509338e-15 128 12            50            5         1.839620

All 12 requested contracts from 1e-8 through 1e-14 passed.

Additional 1e-5000 stress tests:
- requested 1e-16 -> achieved ratio-minus-one about 3.05e-18;
- requested 1e-18 -> achieved ratio-minus-one about 9.20e-20.

## Fail closed

The regression suite includes a deliberately impossible 1e-40 request under
fixed low resource caps.  The solver returns `certified=False`.

## Tests

`test_accuracy_driven.py`: 2/2 PASS, covering 13 certification decisions.

## Critical repair

The multiplicative-ratio acceptance test is evaluated under explicit
high-precision arithmetic.  A preliminary version used default mpmath
precision and could round extremely small ratio-minus-one values to zero.
That acceptance-layer defect is fixed in v1.5.

## Boundary

The contract is rigorous for an exact supplied positive spectrum in the v1.4
interval theorem domain.  Arbitrary floating-point matrix-to-spectrum
certification and interval packetization remain separate layers.
