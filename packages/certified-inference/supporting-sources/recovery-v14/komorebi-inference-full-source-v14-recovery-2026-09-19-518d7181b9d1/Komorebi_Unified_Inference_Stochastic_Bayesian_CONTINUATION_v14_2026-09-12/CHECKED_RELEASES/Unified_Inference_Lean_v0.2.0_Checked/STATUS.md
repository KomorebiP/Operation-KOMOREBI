# Unified Inference Lean — v0.2.0 status

## Checked

- [x] finite Bayesian packet normalization
- [x] finite Bayesian fine-state factorization
- [x] sequential evidence composition
- [x] strong finite Markov lumpability iff intertwining
- [x] powers/polynomial coarse propagation
- [x] block-respecting matrix algebra
- [x] inverse closure for packet-block matrices
- [x] finite direct-sum Kalman covariance/gain algebra
- [x] packet-resolved mean algebra
- [x] packet covariance/Lyapunov closure
- [x] Caputo memory commutation with bounded constant linear maps
- [x] Volterra packet reconstruction
- [x] Volterra convolution path contraction
- [x] finite exponential-memory output identity
- [x] exponential memory-state differential law

## Not yet checked as full manuscript statements

- [ ] measure-theoretic Bayes theorem on arbitrary measurable packets
- [ ] Itô proof of the base moment equations
- [ ] full Gaussian-Bayes/Kalman semantic theorem
- [ ] continuous-time matrix-exponential Markov semigroup identity
- [ ] Volterra resolvent convergence theorem
- [ ] kernel approximation norm bound
- [ ] fractional Laplace-mixture representation
- [ ] complete augmented-state hereditary Kalman theorem
- [ ] seven-part common closure theorem

## Integrity

Final Lean check: `RC=0` with warnings treated as errors.
No `sorry`, `admit`, or custom `axiom` declarations.
