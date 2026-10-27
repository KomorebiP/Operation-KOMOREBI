# Unified Inference Lean status — v0.5.0

## Checked

- finite Bayesian packet normalization/factorization realization
- sequential Bayes/evidence composition
- finite strong lumpability iff exact matrix intertwining
- exact power and polynomial intertwining
- discrete exact residual/Duhamel telescoping
- exact bounded-operator exponential intertwining
- **continuous Duhamel identity for approximate intertwining**
- **continuous contraction error bound `≤ t ‖E‖`**
- packet moment/Lyapunov algebra
- block inverse closure
- direct-sum Kalman mean/covariance/Joseph algebra
- Gaussian block covariance implies packet independence
- constant bounded projector / Caputo commutation
- Volterra packet reconstruction and convolution path law
- scalar/operator kernel approximation certificates
- scalar/operator Volterra factorial iterate bounds and finite-horizon uniform convergence
- exact exponential-memory state lift and ODE law
- explicit augmented memory drift matrix
- recursive augmented-memory Joseph Kalman closure

## Open semantic/foundational blocks

- Itô derivation of the base linear-SDE moment equations
- full conditional-Gaussian proof that linear observation Bayes equals the Kalman update

These are not marked complete by assuming the desired equations.

## Audit

- theorem declarations: 88
- definitions/abbreviations: 53
- structures: 1
- sorry: 0
- admit: 0
- custom axioms: 0
- warning-as-error compile: RC 0
- representative axiom audit: RC 0
