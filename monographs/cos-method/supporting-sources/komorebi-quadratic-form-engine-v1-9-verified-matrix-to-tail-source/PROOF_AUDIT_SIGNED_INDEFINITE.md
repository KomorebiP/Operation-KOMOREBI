# Proof and computation audit — signed / indefinite extension

Date: 2026-09-24

## Exact structural claim

For X~N(0,Sigma) with Sigma PSD and M symmetric, let S=Sigma^(1/2).  The symmetric operator H=SMS has real eigenvalues lambda_j and

    X^T M X  =d=  sum_j lambda_j Z_j^2.

This follows from X=SZ, orthogonal diagonalization of H, and rotational invariance of the standard Gaussian.

**Verdict:** proved as written.

## CGF domain

For nonzero signed weights lambda_j,

    K(s) = -1/2 sum_j log(1-2 s lambda_j)

has real domain

    max_{lambda<0} 1/(2 lambda) < s < min_{lambda>0} 1/(2 lambda).

This is the intersection of the scalar moment-generating domains.

**Verdict:** proved as written.

## Fourier-decay observation

Under a legal exponential tilt theta,

    |phi_theta(t)| = product_j [1 + (2 lambda_j t/(1-2 theta lambda_j))^2]^(-1/4).

With r nonzero coefficients this is O(|t|^(-r/2)).  This explains why the same analytic COS-series certificate can be practical at rank 340 and conservative at rank 4.

**Verdict:** proved asymptotic statement.

## Exact finite-endpoint computation

Q=-0.02 chi2_80 was checked at p=1e-8, 1e-30, 1e-100, and 1e-200.
Maximum absolute log10 error: 2.842e-14 decades.
Maximum certificate: 7.230e-13.
All passed.

**Evidence label:** computationally verified against exact chi-square CDF.

## Mixed high-rank computation

A deterministic rank-340 multiscale spectrum with 180 positive and 160 negative coefficients was tested through log10(p)=-81.891936860562.
Maximum packet/full-grid discrepancy: 2.344e-11 decades.
All five packetized runs passed; largest certificate 7.402e-09.
Independent tilted importance sampling placed all discrepancies within 1.411 Monte Carlo standard errors.

**Evidence label:** certified numerical evaluation plus independent stochastic cross-check.

## Low-rank mixed boundary

For Q=0.07(chi2_2-chi2_2), the exact law is Laplace(0,0.14).  Values through 1e-200 agree to at most 3.056e-09 decades, but the analytic certificate fails because the Fourier tail is too slowly decaying for the current finite-interval bound.

**Verdict:** numerical value validated; certification incomplete for this low-rank mixed regime.

## Strongest safe statement

v1.3 supports central signed/indefinite Gaussian quadratic forms with certificate-gated right-tail evaluation.  Negative finite-endpoint and high-rank mixed-sign examples are strongly validated.  Low-rank mixed-sign certification remains open and is not promoted as solved.
