# Block 31 proof guide

## 1. Finite spinor fields as a genuine Hilbert space

- `HilbertState Site` is `EuclideanSpace ℂ (Site × Fin 4)`.
- `stateToHilbert` and `hilbertToState` identify the existing state type with
  that Euclidean realization.
- `stateHilbertEquiv` proves the algebraic equivalence.
- `stateToHilbert_norm_sq` proves
  \[
  \|\psi\|_{\ell^2}^2=\operatorname{Re}\langle\psi,\psi\rangle_{\rm state}.
  \]

This closes the norm mismatch left explicit in Block 30.  The operator norms in
Block 31 are actual Euclidean `ℓ²` operator norms.

## 2. Exact directional mismatch energy

For two unit-circle links `v` and `u`, the difference of their Clifford shifts
splits into orthogonal positive and negative projector channels.

- `directionalShift_sub_stateIP_re_formula` gives the exact sitewise energy.
- `circle_inv_sub_inv_norm` shows the inverse-link mismatch has the same norm.
- `directionalShift_sub_stateIP_re_le` bounds the energy by `δ²` times the input
  energy whenever every local phase mismatch is at most `δ`.

The orthogonality of the Clifford projectors prevents a volume-dependent cross
term.

## 3. Continuous-operator constant-one estimate

- `directionalShiftDefectHilbertCLM` packages the shift difference as a
  continuous linear map on `HilbertState`.
- `directionalShiftDefectHilbertCLM_norm_le` proves the pointwise norm estimate.
- `directionalShiftDefectHilbertCLM_opNorm_le` lifts it to operator norm.
- `edgeMismatchSup` is the maximum local additive phase mismatch.
- `directionalShiftDefectHilbertCLM_opNorm_le_sup` gives
  \[
  \|S_v-S_u\|\le\max_x\|v(x)-u(x)\|.
  \]

The constant is one and is independent of the number of lattice sites.

## 4. The actual half-cell refinement defect

- `HalfHilbertState` is the fine half-edge Euclidean space.
- `halfStateToHilbert` includes the factor `1/√2` required by half-cell measure.
- `halfStateToHilbert_norm_sq` identifies its norm with the checked half-cell
  inner product.
- `fineEdgeDefectHilbertCLM` is the actual adjacent-scale defect.
- `fineEdgeDefectHilbertCLM_norm_eq_coarse` proves its norm is exactly the norm
  of the reconstructed coarse-link mismatch.
- `fineEdgeDefectHilbertCLM_opNorm_le_sup` supplies the constant-one operator
  estimate for the genuine fine defect.

## 5. Multiplicative reconstruction ratios

- `edgeRatio v u x = v(x)u(x)⁻¹`.
- `edgeRatio_eq_one_iff` proves ratio one is exact reconstruction.
- `edgeMismatch_eq_ratioError` proves
  \[
  \|v-u\|=\|vu^{-1}-1\|.
  \]
- `edgeRatioSup` is the maximum ratio error.
- `fineEdgeDefectHilbertCLM_opNorm_le_ratioSup` is the principal Block 31
  theorem:
  \[
  \|D_{\rm fine}\|_{\ell^2\to\ell^2}
  \le
  \max_x\|E(x)-1\|.
  \]

The quarter-turn witness has ratio supremum two, so the formalization does not
silently identify flat plaquettes with correct edge reconstruction.

## 6. Explicit dyadic sufficient regime

- `dyadicMesh a₀ n = a₀ 2^{-n}` tends to zero.
- `dyadicScaleBudget C n = C 2^{-n}` is summable and tends to zero.
- `summable_dyadicTwoBudget` combines independent edge and curvature channels.
- `tendsto_dyadicTwoBudgetLimit` instantiates the Block 30 global-limit theorem.
- `dist_dyadicTwoBudgetLimit_le_tail` retains the quantitative tail bound.

This is a sufficient summability theorem.  It does not derive the constants or
rates from a concrete gauge connection.

## Boundary

Block 31 proves the scalar operator estimate for a reconstructed directional
edge and its normalized fine defect.  The complete three-axis seven-factor
scalar estimate, physical scale derivation, continuum Hilbert reconstruction,
and continuum Dirac convergence remain open.
