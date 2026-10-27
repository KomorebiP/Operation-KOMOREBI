# Time-Varying Multiscale Stochastic Refinement v0.2.0 — Lean Checked

This release contains two nested finite-time covariance leakage certificates.

## Sharp form

For `D' = A D + D B + R`, Lean proves the exact two-sided Duhamel formula and

\[
\|D(t)\|\le
\|e^{(t-t_0)A}\|\,\|D(t_0)\|\,\|e^{(t-t_0)B}\|
+\int_{t_0}^t
\|e^{(t-s)A}\|\,\varepsilon(s)\,\|e^{(t-s)B}\|\,ds.
\]

For projector-resolved stochastic covariance error, `ε(s)` is the exact sum of norms of fine descendant residual corners.

## Exponential-growth form

If the propagators satisfy

\[
\|e^{uA}\|\le e^{\alpha u},\qquad
\|e^{uB}\|\le e^{\beta u},
\]

then Lean proves

\[
\boxed{
\|D(t)\|
\le e^{(\alpha+\beta)(t-t_0)}\|D(t_0)\|
+\int_{t_0}^t e^{(\alpha+\beta)(t-s)}\varepsilon(s)\,ds.
}
\]

This is then specialized to the multiscale covariance block `C_a D C_b` with the forcing profile

\[
\varepsilon_{ab}(s)=
\sum_{\rho(c)=a,\rho(d)=b}\|F_cR(s)F_d\|.
\]

Thus fine-scale stochastic leakage has a resolution-aware finite-time convolution certificate.

## Formal boundary

The exponential-growth theorem assumes the stated semigroup growth envelopes. It does not claim that arbitrary bounded generators automatically have prescribed rates `α,β`; the sharper semigroup-norm theorem requires no such simplification.

All checked representative theorems depend only on `propext`, `Classical.choice`, and `Quot.sound`.
