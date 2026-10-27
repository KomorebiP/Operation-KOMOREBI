# Unified Inference Lean v0.1.0 — Checked finite core

First Lean formalization checkpoint for the standalone appendix **Unified Projector Calculus for Probability, Inference, Stochastic Dynamics, and Memory**.

## Verified environment

Checked using the preserved Komorebi portable runtime:

- Lean: `4.34.0-rc2`
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- checker: bundled `run.sh check`, which treats warnings as errors
- final return code: `0`

## Inventory

- 35 theorem declarations
- 21 definitions
- 0 `sorry`
- 0 `admit`
- 0 custom `axiom` declarations

Representative `#print axioms` audits report only standard Lean/Mathlib foundations:
`propext`, `Classical.choice`, and `Quot.sound`.

## Block A — finite Bayesian packet calculus

Checked results include:

- exact finite evidence normalizer;
- posterior packet normalization;
- posterior nonnegativity;
- exact sequential evidence composition;
- invariance under a common nonzero likelihood scale;
- finite internal-state packet prior/evidence model;
- `packet mass × conditional packet likelihood = packet evidence`;
- global evidence decomposition `Z = Σᵢ pᵢ ℓᵢ`;
- exact packet posterior factorization
  `pᵢ⁺ = pᵢ ℓᵢ / Σⱼ pⱼ ℓⱼ`;
- global fine-state posterior normalization;
- recovery of the packetwise conditional posterior from the fine posterior.

Boundary: this is a finite discrete realization of the manuscript's Bayesian packet theorem. The full measure-theoretic conditional-law statement is not yet formalized.

## Block B — exact strong Markov lumpability algebra

Checked results include:

- `Intertwines Q C Qbar := Q*C = C*Qbar`;
- propagation through every natural power `Q^n C = C Qbar^n`;
- finite polynomial functional calculus;
- exact coarse row propagation;
- explicit state-to-cell indicator matrix;
- explicit cell-rate definition of strong lumpability;
- construction of a coarse matrix from cell representatives;
- exact theorem, for a surjective finite partition:
  `StrongLumpable Q cell ↔ ∃ Qbar, Q*C = C*Qbar`.

Boundary: power/polynomial propagation is checked. The continuous-time matrix-exponential/semigroup identity is a later analytic block.

## Block C — direct-sum Kalman matrix closure

A general rectangular `BlockRespecting` predicate is formalized. Checked closure properties include:

- zero, addition and subtraction;
- compatible rectangular multiplication;
- transpose;
- identity;
- packet diagonal projectors;
- equivalence mechanism between block support and commutation with packet projectors;
- two-sided inverse of a packet-block square matrix is automatically packet-block.

Using these lemmas, Lean proves block closure of:

- covariance prediction `A P Aᵀ + Q`;
- innovation covariance `H P⁻ Hᵀ + R`;
- Kalman gain `P⁻ Hᵀ S⁻¹`;
- covariance correction `(I-KH)P⁻`;
- the combined finite direct-sum Kalman covariance recursion.

The strongest theorem assumes only the actual two-sided inverse equations for the supplied innovation inverse; its block structure is derived rather than assumed.

Boundary: this checkpoint formalizes the exact finite matrix/covariance closure. A full probabilistic Gaussian-state theorem, conditional expectations, and stochastic process semantics remain separate obligations.

## Next major blocks

1. stochastic first/second moment equations and packet covariance decomposition;
2. continuous-time semigroup consequence of strong lumpability;
3. constant-projector Caputo commutation;
4. Volterra packet reconstruction and resolvent convergence;
5. finite Markovian lift for sums of exponentials;
6. unified memory-filter theorem.

No analytic theorem above is counted as proved merely because its finite algebraic skeleton is checked.
