# Status — Time-Varying Multiscale Stochastic Refinement v0.2.0

- Lean 4.34.0-rc2
- mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- Full warning-as-error check: PASS (RC=0)
- Axiom audit: PASS (RC=0)
- 45 theorem declarations
- 11 definitions
- 2 structures
- 0 `sorry`
- 0 `admit`
- 0 custom axiom declarations

## New in v0.2

In addition to the exact semigroup-weighted Duhamel/multiscale certificate from v0.1, v0.2 proves a scalar exponential-growth-envelope corollary.

If

`‖exp(uA)‖ ≤ exp(αu)` and `‖exp(uB)‖ ≤ exp(βu)`

on the relevant horizon, then

`‖D(t)‖ ≤ exp((α+β)(t-t0)) ‖D(t0)‖
 + ∫ s in t0..t, exp((α+β)(t-s)) ε(s)`.

The theorem is also specialized to a coarse stochastic covariance-error block with `ε(s)` equal to the actual fine-descendant residual norm budget.
