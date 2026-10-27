# Unified Inference Lean v0.4.0 — Checked

Lean normalization checkpoint for **Unified Projector Calculus for Probability, Inference, Stochastic Dynamics, and Memory**.

## Verification

Pinned environment:

- Lean / Lake: `leanprover/lean4:v4.34.0-rc2`
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`

Final source check: **RC = 0**, with the portable checker configured to treat warnings as errors.

Inventory:

- 81 theorem declarations
- 50 definitions/abbreviations
- 1 structure
- 0 `sorry`
- 0 `admit`
- 0 custom `axiom` declarations

Representative `#print axioms` checks report only the standard Lean/Mathlib foundations `propext`, `Classical.choice`, and `Quot.sound`.

## New in v0.4

### Operator-valued Volterra resolvent

For Banach-space operator kernels `K : ℝ → (E →L[ℝ] E)`, the release defines causal operator convolution and iterated convolution powers and proves

`‖K^{*(n+1)}(t)‖ ≤ M^(n+1) t^n / n!`

on a finite horizon whenever `‖K(t)‖ ≤ M`.  It then proves uniform convergence of the operator-valued resolvent series on `[0,T]` by the same factorial majorant used in the scalar theorem.

This upgrades the v0.3 scalar M-test to the operator-valued formulation used by the Volterra/projector calculus.

### Explicit finite-memory augmented state

The release defines the finite augmented coordinate type

`physical state ⊕ (memory mode × physical state)`

and the exact drift corresponding to

`x' = A₀ x + Σᵣ Wᵣ zᵣ`,
`zᵣ' = x - λᵣ zᵣ`.

Lean proves coordinatewise that matrix-vector multiplication by this augmented drift produces exactly those two equations.

### Packet inheritance through the Markovian lift

Memory coordinates inherit the packet label of their underlying physical coordinate.  Lean proves:

- the augmented drift is block respecting if `A₀` and every `Wᵣ` are block respecting;
- physical covariance/process-noise matrices embed as block-respecting augmented matrices;
- a physical observation matrix remains block respecting on the augmented state.

### Recursive augmented Kalman closure

For an arbitrary already-augmented block-respecting covariance `Paug` and process covariance `Qaug`, Lean proves one complete Joseph-form Kalman prediction/update step remains block respecting, deriving block structure of the innovation inverse from its actual two-sided inverse equations.

This recursive version permits nonzero within-packet physical-memory covariance after the first filter step; it is therefore suitable for induction over filtering time rather than only an initialized zero-memory covariance.

A specialized initial-state corollary lifts physical `P` and `Q` with zero memory covariance blocks.

## Retained results from v0.1–v0.3

The single source also retains checked formalizations of:

- finite Bayesian packet factorization and sequential evidence composition;
- finite strong Markov lumpability iff matrix intertwining;
- power/polynomial propagation and an operator-exponential intertwining theorem;
- exact discrete residual propagation for approximate lumping;
- direct-sum Kalman prediction, innovation, gain, mean update, covariance update, and Joseph covariance closure;
- inverse closure for block-respecting matrices;
- packet-resolved linear mean/covariance algebra;
- constant bounded-map commutation with Caputo memory under explicit Bochner-integrability hypotheses;
- Volterra packet reconstruction and packet-path convolution;
- finite exponential-memory output and the FTC-derived memory-state differential law;
- scalar and operator-valued finite-horizon kernel approximation error bounds;
- scalar Volterra factorial bound and uniform resolvent convergence;
- Gaussian packet independence from zero cross covariance and from block-respecting covariance.

## Remaining boundary

This release does **not** claim the entire appendix is formalized.  Major remaining semantic/analytic items include:

1. derivation of the linear SDE moment equations from Itô stochastic integration itself; the pinned Mathlib lacks a sufficiently developed Itô-integral API for the manuscript proof;
2. the full measure-theoretic theorem that linear Gaussian conditioning equals the Kalman update;
3. a continuous-time normed Duhamel bound for approximate Markov lumping (the exact discrete telescoping analogue is checked);
4. integration of the augmented-memory state theorem with a full Gaussian-conditioning/Kalman semantic theorem.

Thus v0.4 closes the operator-valued memory/resolvent layer and the structural augmented-memory Kalman theorem, while keeping the remaining probabilistic semantics explicit.

## Corrected development failures

No failed draft is counted as checked.

- The first operator-resolvent check failed only because the factorial-bound theorem unnecessarily inherited a `CompleteSpace` section assumption.  That assumption was removed; the stronger theorem then passed.
- The first augmented-state definitions left the physical/memory index types implicit in result-only positions, so Lean could not infer them.  The final definitions carry explicit augmented index parameters.
- Initial block proofs applied `BlockRespecting` hypotheses without their row/column indices.  The final proofs pass both indices explicitly.
- The memory-coordinate matrix-vector proof required an explicit two-level `Finset.sum_eq_single` argument for the Kronecker-delta memory block rather than relying on simplification.
- The initial covariance-lift/observation lemmas inherited unused Fintype/DecidableEq assumptions.  Those were explicitly omitted so warning-as-error remains clean.

Every final theorem was rechecked after these corrections.
