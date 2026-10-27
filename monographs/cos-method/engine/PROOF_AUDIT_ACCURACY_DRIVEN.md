# Accuracy-driven rigorous tail solver audit — v1.5

Date: 2026-09-24

## Contract

The public input is an accuracy requirement, not a transform resolution.

Given an exact supplied positive spectrum, threshold \(q\), and requested
relative multiplicative accuracy \(\varepsilon>0\), the solver must return
a probability interval \([p_-,p_+]\) only as certified when

\[
\boxed{
\frac{p_+}{p_-}-1\le\varepsilon.
}
\]

Equivalently, if

\[
\log_{10}p\in[d_-,d_+],
\]

the acceptance condition is

\[
10^{d_+-d_-}-1\le\varepsilon.
\]

The solver is fail-closed: if the resource caps are reached before this
inequality is proved, the result is marked uncertified and the unresolved
interval is returned instead of an accuracy claim.

## Refinement variables

The adaptive solver controls:

- COS mode count \(K\);
- support scale \(L\), hence the finite interval endpoint \(U\);
- interval arithmetic precision.

The tilt and Chernoff parameters are redesigned whenever \(L\) changes.

A candidate is accepted only from the interval enclosure produced by the
v1.4 directed-rounding backend plus the proved support/alias and infinite-mode
remainders.

## Refinement logic

1. Evaluate the current rigorous interval.
2. Compute the multiplicative ratio from the interval width at controlled
   high precision.
3. If the arithmetic-only interval width is material, increase interval
   precision.
4. Otherwise refine whichever analytic contribution is larger:
   omitted-mode error increases \(K\), support/alias error increases \(L\).
5. Stop only when the requested multiplicative inequality is proved.
6. If all resource caps are exhausted, return certified=False.

## Acceptance-check bug found and repaired

The first implementation converted a \(10^{-15}\)-scale log interval width
to \(10^w-1\) using mpmath's default global precision.  At sufficiently
small widths this rounded the ratio to zero.

The interval itself remained valid, but the acceptance decision could be
overconfident.

v1.5 repairs the decision by evaluating

\[
\operatorname{expm1}(\log(10)\,w)
\]

inside an explicit high-precision context.  The regression suite includes
accuracy requests down to \(10^{-14}\), and a separate stress run reaches
\(10^{-18}\).

## Exact scaled-chi-square control

The deterministic control is

\[
Q=0.02\chi^2_{80}.
\]

Thresholds corresponding to \(10^{-100}\), \(10^{-1000}\), and
\(10^{-5000}\) are generated at high precision and independently checked by
the finite even-df gamma-tail formula used in v1.4.

For each depth the adaptive solver was asked to certify

\[
10^{-8},\quad10^{-10},\quad10^{-12},\quad10^{-14}
\]

relative multiplicative accuracy.

All 12 contracts passed.

At \(10^{-5000}\):

- request \(10^{-8}\): achieved about \(3.19\times10^{-10}\);
- request \(10^{-10}\): achieved about \(7.70\times10^{-11}\);
- request \(10^{-12}\): achieved about \(3.48\times10^{-15}\);
- request \(10^{-14}\): achieved about \(3.48\times10^{-15}\).

A further stress run requested \(10^{-16}\) and \(10^{-18}\):

- request \(10^{-16}\): achieved about \(3.05\times10^{-18}\);
- request \(10^{-18}\): achieved about \(9.20\times10^{-20}\).

The solver automatically increased support scale and, when needed, mode count.

## Fail-closed test

An intentionally impossible request was run with a \(10^{-40}\) relative
accuracy target while \(K\), \(L\), and interval precision were pinned at
small caps.

The solver returned certified=False with an explicit failure reason.

## Evidence label

For exact supplied positive spectra within the v1.4 theorem domain, the
accuracy-driven wrapper is a certified refinement controller around the
directed-rounding interval backend.

The guarantee remains conditional on correctness of the interval arithmetic
library and does not yet include arbitrary matrix-to-spectrum rounding error.
