# Status — Gaussian–Kalman Bayesian Conditioning v0.1.0

## Closed and kernel-checked

- [x] scalar Gaussian completing-square identity
- [x] scalar Gaussian normalization-constant identity
- [x] exact prior × likelihood = evidence × posterior density factorization
- [x] ENNReal density factorization
- [x] Gaussian likelihood kernel
- [x] explicit scalar Kalman posterior kernel
- [x] Markov-kernel instances
- [x] exact observation marginal `N(m,p+r)`
- [x] prior/likelihood joint density
- [x] evidence/posterior joint density
- [x] coordinate-swap transport of product-Lebesgue density
- [x] exact joint disintegration identity
- [x] canonical Bayesian posterior = scalar Kalman posterior, evidence-a.e.
- [x] pointwise normalized Bayes density = Kalman Gaussian density
- [x] pointwise normalized Bayes measure = Kalman Gaussian posterior measure

## Open / not claimed

- [ ] arbitrary scalar observation coefficient `h` in `Y=hX+ε`
- [ ] arbitrary finite-dimensional observation matrix `H`
- [ ] singular covariance cases beyond the positive-variance theorem stated here
- [ ] integration of this semantic bridge into the earlier operator-valued multiscale posterior perturbation theorem

## Integrity

- warning-as-error compile: PASS, RC=0
- representative axiom audit: PASS, RC=0
- `sorry`: 0
- `admit`: 0
- custom axioms: 0
