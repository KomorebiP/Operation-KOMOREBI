# Generalization note — Komorebi Quadratic-Form Engine v1.1

The engine is no longer defined by SKAT.

## Central positive core

For

\[
X\sim N(0,\Sigma),\qquad M\succeq0,
\]

the statistic

\[
Q=X^\top M X
\]

reduces exactly to

\[
Q\overset d=\sum_j\lambda_j Z_j^2,
\]

where the \(\lambda_j\) are the nonzero eigenvalues of

\[
\Sigma^{1/2}M\Sigma^{1/2}.
\]

Equivalent inputs are:

- the spectrum itself;
- a PSD matrix;
- a dense factor \(A\);
- replayable streamed factor blocks \(A=[A_1\cdots A_B]\);
- the pair \((\Sigma,M)\).

## Noncentral positive extension

For

\[
X\sim N(\mu,\Sigma),
\qquad
M\succeq0,
\]

write

\[
H=\Sigma^{1/2}M\Sigma^{1/2}
=
V\Lambda V^\top
\]

and

\[
c=V^\top\Sigma^{1/2}M\mu.
\]

Then

\[
Q
\overset d=
q_0+
\sum_{\lambda_i>0}
\lambda_i
\chi^2_1\!\left(
(c_i/\lambda_i)^2
\right),
\]

with

\[
q_0
=
\mu^\top M\mu
-
\sum_{\lambda_i>0}
c_i^2/\lambda_i
\ge0.
\]

This deterministic shift is necessary when the covariance is singular.

## Application classes

The same numerical core applies whenever the mathematical model reduces to a
positive Gaussian quadratic form, including kernel tests, variance-component
tests, Gaussian-process quadratic statistics, covariance-component tests,
weighted residual energies, spectral goodness-of-fit tests, matched-subspace
energy tests, and SKAT-like association tests.

The engine solves the numerical quadratic-form problem once the PSD Gaussian
representation is valid.  Model-specific finite-sample calibration remains an
application-layer question.

## Current boundary

v1.1 covers:

- central positive Gaussian quadratic forms;
- noncentral positive Gaussian quadratic forms;
- memory-bounded streamed factors;
- polyphase/Krylov scheduling;
- residual moment certification and exact completion;
- hardened log-domain extreme-tail evaluation.

Signed/indefinite forms exist in the research code but remain outside the
minimal production API until their packetized certificates receive the same
hardening pass.
