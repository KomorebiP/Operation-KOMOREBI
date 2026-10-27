# Bayesian Multiscale Kalman Posterior Perturbation v0.1.0 — Lean checked

This release extends the checked time-varying multiscale stochastic-refinement development into the **linear-Gaussian/Kalman posterior update** itself.

## Verification environment

- Lean / Lake: `leanprover/lean4:v4.34.0-rc2`
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- warnings treated as errors
- final source check: RC = 0
- axiom audit: RC = 0
- `sorry`: 0
- `admit`: 0
- custom `axiom`: 0

The combined source contains 73 theorem declarations, 21 definitions, and 2 structures. Relative to the retained v0.2 time-varying multiscale source, this release adds 28 theorem declarations and 10 definitions.

## New Bayesian/Kalman perturbation layer

For Hilbert state/observation spaces, define

`A(K,H) = I - K H`,

`J(K,H,P,R) = A P A* + K R K*`

(the Joseph posterior covariance),

`S(H,P,R) = H P H* + R`

(the innovation covariance), and

`K(P,H,Sinv) = P H* Sinv`.

### Exact Joseph posterior residual identity

Lean proves an exact six-term telescoping identity for

`J(K,H,P,R) - J(K0,H0,P0,R0)`.

The six terms separately record closed-loop residual, prior-covariance residual, gain residual, and observation-noise residual contributions. No higher-order term is hidden; the exact products are retained inside the factors.

### Innovation and inverse conditioning

Lean proves

`S - S0`

as an exact three-product-plus-noise residual identity, with a corresponding operator norm bound.

Given inverse equations in the needed orientations, Lean proves

`Sinv - Sinv0 = Sinv (S0 - S) Sinv0`

and

`||Sinv-Sinv0|| <= ||Sinv|| ||S-S0|| ||Sinv0||`.

Thus poor innovation conditioning appears explicitly rather than being suppressed.

### Gain perturbation

Lean proves the exact gain residual decomposition

`K-K0 = (P-P0) H* Sinv + P0 (H*-H0*) Sinv + P0 H0* (Sinv-Sinv0)`

and an end-to-end norm budget driven by `P-P0`, `H-H0`, `R-R0`, and the two innovation inverse norms.

### End-to-end posterior covariance bound

Lean then composes the innovation, inverse, gain, closed-loop, and Joseph inequalities. The theorem

`josephPosteriorCov_sub_norm_le_residual_budget`

bounds the complete posterior covariance error using named prior/observation/noise residuals and actual innovation inverse conditioning factors.

### Posterior mean

For

`m+ = m + K (y - H m)`,

Lean proves an exact residual identity and an end-to-end norm bound driven by prior-mean error, observed-data error, observation-model error, and the derived gain budget.

## Multiscale posterior layer

For an orthogonal projector refinement `F -> C`, Lean proves for the posterior covariance error operator `Epost`:

- exact coarse-to-fine block refinement;
- coarse block zero iff every fine descendant posterior-error block is zero;
- coarse block nonzero iff some fine descendant posterior-error block is nonzero;
- coarse block norm bounded by the sum of fine descendant norms;
- if coarse projectors are contractive, every coarse posterior-error block is bounded by the global end-to-end named-residual posterior budget.

This gives an adaptive posterior-refinement criterion: nonzero coarse posterior covariance error is equivalent to the existence of a nonzero fine descendant error channel.

## Boundary

This is a rigorous perturbation/stability theorem for the **Kalman/Joseph posterior map**, which is the posterior mean/covariance update used in linear-Gaussian Bayesian filtering. It does **not** by itself formalize the measure-theoretic theorem identifying that update with conditional Gaussian Bayes. That semantic conditioning theorem remains a separate obligation.

No claim of literature priority or novelty is made by this package.
