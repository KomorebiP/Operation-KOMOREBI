# Verified matrix-to-spectrum and matrix-to-tail audit - v1.9

Date: 2026-09-24

## Claim

For a binary64 factor A, treated as the exact dyadic matrix stored in memory,
an untrusted candidate eigensystem can be post-certified and propagated into a
rigorous positive quadratic-form tail interval.

## Spectral theorem

Let H=A A^T, D=diag(d_i)>=0, and B=Q D Q^T.  If

    ||Q^T Q-I||_2 <= eta < 1
    ||H-B||_2 <= rho,

then for ordered eigenvalues

    max(0,(1-eta)d_i-rho) <= lambda_i(H) <= (1+eta)d_i+rho.

Proof: S=Q^TQ obeys (1-eta)I <= S <= (1+eta)I.  B and
D^(1/2) S D^(1/2) have the same eigenvalues, so Loewner monotonicity bounds
the eigenvalues of B by (1+-eta)d_i.  Weyl then adds +-rho.

The implementation encloses Q^TQ-I and H-QDQ^T entrywise with mpmath.iv and
uses ||.||_2 <= ||.||_F.  The high-precision eigensolver is a candidate
generator only.

## Tail propagation

Coefficient-wise intervals are propagated using the common-normal coupling:

    sum l_i Z_i^2 <= sum lambda_i Z_i^2 <= sum u_i Z_i^2  almost surely.

Thus the true tail is bracketed by rigorous positive-tail evaluations at the
lower and upper spectra.

## Float semantics

Every binary64 input entry is converted by its exact integer ratio.  The
certificate therefore concerns the exact matrix represented by the stored
binary64 values.  It does not claim an interval for an unknown pre-rounding
physical or statistical quantity.

## Serialization defect found and repaired

An early v1.9 draft converted interval endpoints through default-precision
mpmath strings.  Bounds of the form 1 +- 1e-49 could collapse to the literal
string "1.0".  The theorem was unaffected, but the serialized coefficient
interval could be narrowed incorrectly.

The production implementation now preserves the literal outward endpoint
strings emitted by the interval layer.  A dedicated regression test requires
that the leading exact eigenvalue 1 lie strictly inside a nonzero interval.

## Random dense spectral audit

Exact binary64 factors of sizes 12x18, 20x30, and 28x36 were tested against
independently recomputed high-precision eigenvalues of the exact dyadic Gram
matrices.

All eigenvalues were contained in all three cases.  The largest relative
interval width was approximately 1.20e-56.

## End-to-end matrix-defined tail

A dense 64x64 factor uses an exact normalized Hadamard basis and binary
singular values 1, 0.75, 0.5, and 0.25, each repeated 16 times.

The spectral postcheck produced approximately

    eta <= 1.65e-49
    rho <= 9.18e-50.

At q=131.33201485100517, with p near 1e-16:

- requested relative accuracy 1e-10 -> achieved 2.60e-12, certified;
- requested relative accuracy 1e-12 -> achieved 4.09e-15, certified.

The 1e-12 final log10 interval is approximately

    [-15.99999999999996625, -15.99999999999996447].

## Evidence boundary

This closes correctness for moderate binary64 factors.  The current verifier
uses a full dense candidate eigenbasis and therefore is not yet the scalable
streaming solution for very large factors.  That requires a verified
range-core/residual-completion variant.
