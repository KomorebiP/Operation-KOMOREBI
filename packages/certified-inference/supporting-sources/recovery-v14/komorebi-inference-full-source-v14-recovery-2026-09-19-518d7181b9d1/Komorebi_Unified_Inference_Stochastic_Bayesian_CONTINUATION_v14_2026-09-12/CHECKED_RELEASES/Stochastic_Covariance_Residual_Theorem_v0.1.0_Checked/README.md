# Stochastic Covariance Residual Theorem v0.1.0 — Lean checked

This experimental theorem block extends the Unified Inference Lean development with a residual/stability theorem for the linear stochastic covariance (Lyapunov) equation.

## Main exact identities

For a baseline drift/noise pair `A0,Q0`, residuals `RA,RQ`, actual covariance `P`, baseline covariance `P0`, and error `D=P-P0`, Lean proves

`covarianceRHS (A0+RA) P (Q0+RQ) - covarianceRHS A0 P0 Q0`

is exactly

`covarianceRHS A0 D 0 + covarianceRHS RA P RQ`,

i.e.

`A0 D + D A0ᵀ + RA P + P RAᵀ + RQ`.

It also proves that if `P0` is packet respecting, every off-packet covariance entry of `P` is exactly the corresponding covariance-error entry.

## Off-packet leakage certificate

At a packet-respecting covariance state, the instantaneous covariance created between distinct packets is controlled solely by drift/noise residuals. Lean proves the explicit packet-localized bound

`|covarianceRHS (A0+RA) P (Q0+RQ) i j|`

is at most the sum of residual drift couplings into the target packet, residual drift couplings out of the source packet, and `|RQ i j|`.

## Operator-norm stability inequality

In any normed star algebra with isometric involution, Lean proves

`‖Δ covariance drift‖ ≤ 2‖A0‖‖P-P0‖ + 2‖RA‖‖P‖ + ‖RQ‖`.

This separates propagation of already accumulated covariance error from fresh model-residual forcing.

## Important rejected attempt

A first finite-horizon theorem assumed the *actual* covariance remained packet respecting on the entire interval. That assumption makes every cross-packet covariance entry identically zero, so the theorem would have been technically true but scientifically vacuous. It was discarded and is not included in this package. The corrected error-dynamics theorem keeps the accumulated off-packet covariance error explicitly.

## Verification

- Lean 4.34.0-rc2 portable checker
- `-DwarningAsError=true`
- source check: RC = 0
- axiom audit: RC = 0
- `sorry`: 0
- custom `axiom`: 0
- audited central theorems depend only on `propext`, `Classical.choice`, and `Quot.sound`

This package establishes the theorem formally. It does **not** establish literature priority or novelty.
