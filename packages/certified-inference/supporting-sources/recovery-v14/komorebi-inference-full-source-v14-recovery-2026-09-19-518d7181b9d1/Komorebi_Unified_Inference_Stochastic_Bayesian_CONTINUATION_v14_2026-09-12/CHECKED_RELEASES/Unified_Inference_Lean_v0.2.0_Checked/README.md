# Unified Inference Lean v0.2.0 — Checked

This checkpoint formalizes the finite and analytic core of the **Unified Projector Calculus for Probability, Inference, Stochastic Dynamics, and Memory** appendix.

## Verification

The final source was checked with warnings promoted to errors using the preserved portable runtime:

- Lean / Lake: `leanprover/lean4:v4.34.0-rc2`
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- final compiler exit code: `0`

Source inventory:

- 55 theorem declarations
- 33 definitions
- 1 structure
- 0 `sorry`
- 0 `admit`
- 0 custom `axiom` declarations

Representative `#print axioms` audits report only ordinary Lean/Mathlib foundations: `propext`, `Classical.choice`, and `Quot.sound`.

## Checked theorem families

### 1. Finite Bayesian packet factorization

The finite model proves:

- evidence normalization;
- posterior nonnegativity;
- exact packet posterior formula;
- global fine-state posterior normalization;
- within-packet posterior recovery;
- sequential evidence composition;
- invariance under a common nonzero likelihood scale.

This is a finite discrete realization of the manuscript's measure-theoretic Bayes packet theorem. The general measurable-space/integral version is not claimed here.

### 2. Strong Markov lumpability

For finite partitions, Lean proves the row-cell-rate definition of strong lumpability is equivalent to existence of a coarse matrix `Qbar` satisfying `Q C = C Qbar`. It also proves:

- `Q^n C = C Qbar^n` for every natural `n`;
- finite polynomial functional calculus intertwining;
- exact finite coarse propagation.

The full analytic matrix-exponential/continuous-time semigroup identity remains a separate step.

### 3. Direct-sum Kalman algebra

Lean proves exact block closure of:

- rectangular packet-compatible matrix products;
- transpose;
- addition/subtraction;
- covariance prediction `A P Aᵀ + Q`;
- innovation covariance `H P Hᵀ + R`;
- Kalman gain with a supplied inverse;
- covariance correction.

It additionally proves that any actual two-sided inverse of a block-respecting square matrix is automatically block respecting. Therefore block structure of the innovation inverse is derived from inverse equations rather than assumed.

The full probabilistic Gaussian-Bayes semantics and the complete Joseph-form/mean-update theorem are not yet claimed.

### 4. Linear stochastic moment packet algebra

Once the standard linear-SDE moment equations are supplied, Lean proves:

- exact source-packet decomposition of the mean equation;
- entrywise covariance/Lyapunov equation;
- block closure of `A P + P Aᵀ + Q`;
- exact vanishing of off-diagonal covariance tangents under independent packet hypotheses.

Derivation of the base moment equations from Itô calculus itself remains outside this checkpoint.

### 5. Caputo memory

For Banach-space-valued supplied derivative data, Lean defines the normalized Caputo memory

`(Gamma (1-alpha))^-1 • ∫_0^t (t-s)^(-alpha) • dx(s) ds`

and proves every bounded time-independent continuous linear map commutes with it, under the explicit interval-integrability hypothesis. An idempotent bounded map therefore preserves its Caputo packet.

The derivative-existence/regularity theorem linking supplied `dx` to an arbitrary function `x` remains a separate analytic interface.

### 6. Volterra packet reconstruction

For a finite complete family of bounded projectors, Lean proves the Bochner-integral identity

`B_i ∫ K(t-s)x(s) ds = Σ_j ∫ B_i K(t-s) B_j x(s) ds`

under explicit interval-integrability hypotheses. It then proves the packet form of a supplied global Volterra equation and exact state reconstruction.

### 7. Volterra path contraction

For operator kernels `K` and `L`, source packet `j`, and target packet `i`, Lean proves the convolution path decomposition as a sum over intermediate packets `k`. This is the memory analogue of transfer-block composition.

### 8. Exact finite exponential-memory lift

For finite rates and bounded operator weights, Lean proves both halves of the exact Markovian lift:

1. the memory output equals the finite sum `Σ_r W_r z_r(t)`;
2. from the integral definition of `z_r` and FTC hypotheses,
   `d z_r / dt = x(t) - rate_r • z_r(t)`.

Thus the finite exponential memory state law is derived, not postulated.

## Remaining high-value blocks

- Itô derivation of the mean/covariance equations;
- full Gaussian-Bayes Kalman theorem, including means and Joseph covariance;
- analytic matrix-exponential semigroup form of exact Markov lumping;
- finite-horizon Volterra resolvent convergence and norm estimates;
- kernel-approximation `L1 × L∞` error bound;
- fractional-kernel Laplace-mixture representation;
- full unified augmented-state memory-filter theorem;
- final seven-part closure theorem in a single Lean namespace.

