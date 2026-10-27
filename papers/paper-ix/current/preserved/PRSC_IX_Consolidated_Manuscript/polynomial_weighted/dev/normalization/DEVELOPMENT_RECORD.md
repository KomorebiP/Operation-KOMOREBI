# Weighted polynomial normalization development

`PolynomialWeightedNormalization.lean` derives the contraction polynomial from the actual system, its actual Jacobian, an integral scalar inverse certificate, and its residual divisibility. It does not assume a polynomial normalization identity.

Observed development runs:

1. `attempt_01.log`: FAIL. All structural, derivative, divisibility, and exponent identities closed, but the final `linear_combination` used the constant factorization equality with the wrong sign. The residual was twice the difference of that equality.
2. `attempt_02.log`: PASS after reversing that equality's multiplier. Process exit code 0 and no output under the warnings-as-errors runner.

The theorem has the original strict threshold `2 * s < r`. It retains the constant vector's precision `p^(r-(2*s+1))` and proves the polynomial remainder vanishes at zero.

Pinned Lean 4.34.0-rc2, one thread, 240-second timeout, default heartbeats, and the mandated `LD_PRELOAD`/`TMPDIR=/dev/shm` environment were used.

Frozen source SHA-256: `3b7ac03ae8c15ff0150f4cc98fc5ced67f285e16ec659400dcddec5585614411`.

Declarations: 2 theorems. Final cumulative gate and dependency audit are managed by the parent task.
