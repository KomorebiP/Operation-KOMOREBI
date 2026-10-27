# Unified Projector Calculus for Probability, Inference, Stochastic Dynamics, and Memory
## Lean normalization v0.3.0 — Checked

This checkpoint consolidates the finite algebraic, analytic-memory, Markov, Kalman,
and Gaussian-packet portions currently formalized from the Unified Inference / Memory appendix.
It is deliberately explicit about which manuscript semantics are proved and which remain outside
the available Lean/Mathlib infrastructure.

### New relative to v0.2

- exact approximate-lumpability residual propagation through every finite power;
- bounded-operator exponential intertwining, including time scaling;
- full Joseph covariance block closure from an actual two-sided innovation inverse;
- packetwise Kalman mean reconstruction;
- scalar and operator-valued L1-L∞ memory-kernel error certificates;
- factorial bound for causal Volterra convolution powers;
- uniform convergence of the scalar Volterra resolvent series on every finite horizon;
- jointly Gaussian zero-cross-covariance implies independent packet vectors;
- direct bridge from a block-respecting covariance matrix to Gaussian packet independence.

### Formalization philosophy

No bounded numerical computation is used as a substitute for a universal theorem. Analytic claims
carry their explicit interval-integrability, continuity, completeness, or bounded-operator hypotheses.
Where the current Mathlib API is missing an essential semantic layer (notably Itô calculus and
linear-Gaussian conditioning), the source stops at the strongest theorem actually kernel-checked.

See `STATUS.md` for the theorem-family crosswalk and exact remaining boundary.
