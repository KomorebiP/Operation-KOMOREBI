# Komorebi Quadratic-Form Engine v1.3

A general engine for Gaussian quadratic forms with memory-bounded structural solvers and extreme-tail evaluation.

## Central positive

`PositiveQuadraticFormEngine` represents

    Q = sum lambda_j Z_j^2,  lambda_j >= 0.

It accepts spectra, PSD matrices, factors, streamed factor blocks, and central Gaussian quadratic forms.

## Central signed / indefinite

`SignedCentralQuadraticFormEngine` represents

    Q = sum lambda_j Z_j^2

with positive and negative coefficients.  It accepts a signed spectrum, a symmetric operator, or `(Sigma, M)` with `Sigma` PSD and `M` symmetric.

The right-tail production path is certificate gated.  Negative-only finite-endpoint forms are certified through 1e-200 in the included exact controls.  A rank-340 mixed-sign multiscale spectrum is certified to approximately 1e-82.

Low-rank mixed-sign forms are a documented boundary: exact-control values may be accurate while the current COS-series certificate rejects them.

## Positive noncentral

`NoncentralPositiveQuadraticFormEngine` reduces

    X ~ N(mu, Sigma),  Q = X^T M X,  M PSD

to a deterministic shift plus weighted noncentral chi-square components.

## Structural layers

The package also contains the polyphase light-cone scheduler, residual spectral certificates, exact residual completion, and log-domain packet hardening used by the manuscript.
