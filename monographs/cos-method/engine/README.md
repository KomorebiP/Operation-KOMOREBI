# Komorebi Quadratic-Form Engine v1.1

A general-purpose engine for central and noncentral **positive Gaussian
quadratic forms** with memory-bounded factor construction and certified
extreme-tail evaluation.

## Central form

\[
Q=\sum_j\lambda_jZ_j^2,\qquad \lambda_j\ge0.
\]

Inputs may be:

- an explicit spectrum;
- a PSD matrix;
- a dense factor;
- replayable streamed factor blocks;
- or \(X\sim N(0,\Sigma)\), \(Q=X^\top MX\), \(M\succeq0\).

## Noncentral form

For \(X\sim N(\mu,\Sigma)\), \(M\succeq0\), the engine reduces the statistic to

\[
Q=q_0+\sum_j \lambda_j\chi^2_1(\delta_j)
\]

with an exact deterministic shift \(q_0\) when required by singular covariance.

## Structural solver layer

The package also carries the generic:

- approximate polyphase light cone;
- certified phase-pruning scheduler;
- spectral/tail bridge;
- residual trace/moment certificate;
- exact streamed residual completion.

## Tail hardening

The central packet certificate uses log-sum-exp arithmetic for its deepest
growth/error accumulation.  Fixed-grid references are explicitly refined
rather than assumed exact.

## Scope

v1.1 is production-oriented for positive central and positive noncentral
Gaussian quadratic forms.  Signed/indefinite generalized forms remain a
separate research API for now.


## v1.4 directed-rounding enclosure

`interval_kcos.py` adds a first rigorous positive-central backend for exact
supplied spectra of rank greater than two.

It combines:
- directed-rounding interval evaluation of the finite tilted COS transform;
- directed-rounding evaluation of the exponential prefactor;
- a tilted Chernoff support/periodization-alias bound;
- a proved power-law bound for all omitted COS modes.

The exact control `0.02 * chi2_80` is independently interval-evaluated by its
finite even-df gamma-tail formula.  The K-COS enclosure overlaps that exact
interval at `1e-100`, `1e-1000`, and `1e-5000`.

At `1e-5000`, the log10 enclosure width is about `3.37e-11` decades,
corresponding to a multiplicative probability ratio of approximately
`1 + 7.75e-11`.

The current theorem starts from an exact decimal spectrum.  Verified
matrix-to-spectrum linear algebra and interval packetization remain separate
future layers.


## v1.5 accuracy-driven contract

The rigorous positive-tail API can now be driven by a requested relative
multiplicative accuracy rather than by transform parameters.

```python
result = certified_positive_logsf(
    q_decimal,
    eigenvalue_decimals,
    relative_accuracy="1e-12",
)
```

A result is labeled certified only if the returned probability interval proves

\[
p_+/p_- - 1 \le \varepsilon_{\rm requested}.
\]

The controller adapts COS mode count, support scale, and interval precision.
If resource caps are reached first, it returns `certified=False` and preserves
the unresolved interval.
