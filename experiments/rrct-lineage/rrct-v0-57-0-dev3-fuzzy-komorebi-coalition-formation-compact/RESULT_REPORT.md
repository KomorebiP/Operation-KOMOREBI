# RRCT v0.57 Fuzzy Komorebi Coalition Formation Result Report

## Status

`V057_FROZEN_ENDPOINTS_MET`

All **22 of 22** frozen endpoints passed across eight untouched seeds and 32 trained models.

## Result

The learned fuzzy packet model achieved:

- mean MSE: **0.000511**
- held-out central-blend MSE: **0.001130**
- crisp-task MSE: **0.000047**
- membership-to-causal-effect correlation: **0.5475**
- idempotence-to-target-fuzziness correlation: **0.9171**

The exact hard projection of the true memberships had zero error on crisp tasks but held-out blend MSE **0.054644**. Hardening the learned fuzzy memberships increased the same error by **74.4 times**.

The unrestricted direct-edge model achieved mean MSE **0.000263**, outperforming the structured factorization. The result therefore favors graded relational structure while leaving direct attention as a stronger prediction-only baseline.

## Mathematical result

The learned fuzzy packets

\[
E_k=\operatorname{diag}(U_{:k})
\]

were positive and formed an exact numerical partition of unity. They also supported

\[
T=\sum_{i,j}E_iTE_j
\]

with maximum relative reconstruction error **3.26 × 10⁻⁷**, despite being non-idempotent on overlap tasks.

## Claim boundary

This is a synthetic terminal-action result. It does not establish a biological brain mechanism, unique superiority of Komorebi factorization, functional awareness, consciousness, sentience, or valence.
