# Centered Dirac continuation: exact target contract

Base checkpoint: v0.50.0-g1, the checked generator overlay on the immutable
Block 49 project. This contract concerns the continuum Fourier family in the
generator chapter, Sections 3 and 4. It does not replace the same infinite
coefficient space with a changing sampled lattice.

## Objects and conventions

- Mode set: `Fin 3 → ℤ`, with physical momenta `k_j = 2π n_j`.
- Spinors: the existing Euclidean complex four-spinor Hilbert space.
- Coefficients: the existing `CoeffL2 = ℓ²(Mode, HilbertSpinor)`.
- Physical fields: the existing torus `L²` spinors and `torusFourierEquiv`.
- Mass: every real `m`, including zero and negative mass.
- Spacing: every real nonzero `h`, including negative spacing.
- Inner product: complex, linear in its second argument.
- Continuum `H`: the existing maximal `continuumDiracPMap`; its domain is
  equivalent to the first-order Fourier summability condition.
- Centered symbol: the existing `centralHilbertModeOperator`, using
  `sinQuot k h`. At zero this *modal* function is filled by the continuum
  value. That does not make the infinite-space Hamiltonian bounded at zero.
- Evolution: the existing `centralCoeffPropagator` and
  `continuumCoeffPropagator`, with the sign `exp(-itH)`.

## Required conclusions

1. For each `h ≠ 0`, construct a bounded complex-linear operator on all of
   `CoeffL2`, with exactly the existing centered modal action. Prove symmetry
   or equivalently bounded self-adjointness and
   `‖H_h‖ ≤ sqrt (m² + 3 / h²)`.
2. For each vector in the *full maximal continuum domain*, prove
   `H_h f → H f` in coefficient norm as `h → 0` through nonzero real values.
   A right-sided limit alone is weaker than the target.
3. For each `z : ℂ` with `z.im ≠ 0`, construct the actual centered and
   continuum resolvents, prove their inverse identities, prove that the
   continuum resolvent lands in the maximal domain, and establish the
   `1 / |z.im|` norm bound.
4. Prove the resolvent-identity estimate
   `‖R_h(z)f - R(z)f‖ ≤ |Im z|⁻¹ ‖(H-H_h) R(z)f‖`, and strong convergence
   for every coefficient vector. Resolvent existence may not merely be an
   extra hypothesis replacing the requested construction.
5. Define the exact third-order spatial moment by
   `M3(f)² = Σ_n (Σ_j |k_j|⁶) ‖f_n‖²`. Require summability, not only a
   totalized infinite-sum expression. Prove that this assumption supplies
   the continuum-domain witness needed to form `Hf`.
6. Prove, for every nonzero real `h`, the sharp-constant generator bound
   `‖H_h f - Hf‖ ≤ h² M3(f) / 6`.
7. Prove, for every real `t`, the propagator bound
   `‖U_h(t)f-U(t)f‖ ≤ |t| h² M3(f) / 6`. No cross-commutation hypothesis
   between `H_h(n)` and `H(n)` may be introduced.
8. Prove the compact-time bound with an explicit `0 ≤ T` and transport the
   convergence and bounds through the actual Fourier isometry to physical
   torus fields.

## Completion boundary

Acceptance requires actual fresh Lean compilation, declaration and recursive
axiom coverage, correct expected rejection controls, preserved exact inputs,
and a source review. This mathematical audit is not such a compiler run.

Still separate: abstract unbounded functional-calculus API linkage, finite-grid
sampling/interpolation and aliasing, interactions, dynamical gauge fields,
empirical interpretation, and the cosmological production obligations.

## Local manuscript clarification

The displayed physical compact-time supremum must quantify `T ≥ 0`. For
negative `T` the index set is empty, so a real-valued totalized supremum need
not satisfy the displayed negative upper bound. The pointwise statement
under `|t| ≤ T` has no such ambiguity. This is a hypothesis clarification,
not a change to the substantive rate theorem.
