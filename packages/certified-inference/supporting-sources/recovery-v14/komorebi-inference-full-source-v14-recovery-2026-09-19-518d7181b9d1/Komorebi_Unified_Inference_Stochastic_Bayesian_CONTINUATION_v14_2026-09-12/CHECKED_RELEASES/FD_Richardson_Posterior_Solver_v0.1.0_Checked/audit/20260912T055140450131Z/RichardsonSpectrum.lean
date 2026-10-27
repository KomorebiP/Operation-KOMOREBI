import Komorebi.FDInnovationConditioning
import Mathlib.Analysis.Matrix.PosDef

noncomputable section
set_option autoImplicit false
namespace Komorebi.GainSolver
open Matrix Komorebi.FiniteDimensionalGaussianKalman
open scoped RealInnerProductSpace
variable {κ : Type*} [Fintype κ] [DecidableEq κ]

/-- A matrix eigenvector is an eigenvector for its genuine Euclidean operator. -/
theorem eigenvector_action (S : Matrix κ κ ℝ) (hS : S.IsHermitian) (i : κ) :
    matrixCLM S (hS.eigenvectorBasis i) = hS.eigenvalues i • hS.eigenvectorBasis i := by
  ext j
  exact congrFun (hS.mulVec_eigenvectorBasis i) j

/-- Quadratic coercivity bounds each eigenvalue; there is no numerical spectral assumption. -/
theorem eigenvalue_lower (S : Matrix κ κ ℝ) (hS : S.IsHermitian) (σ : ℝ)
    (hs : QuadraticLowerBound S σ) (i : κ) : σ ≤ hS.eigenvalues i := by
  have h := hs (hS.eigenvectorBasis i)
  rw [eigenvector_action] at h
  simpa only [inner_smul_right, real_inner_self_eq_norm_sq,
    hS.eigenvectorBasis.orthonormal.1 i, one_pow, mul_one] using h

/-- A positive semidefinite matrix has nonnegative trace. -/
theorem psd_trace_nonneg (S : Matrix κ κ ℝ) (hS : S.PosSemidef) : 0 ≤ S.trace := by
  rw [hS.isHermitian.trace_eq_sum_eigenvalues]
  exact Finset.sum_nonneg (fun i _ => hS.eigenvalues_nonneg i)

/-- The trace is a certified upper bound on each PSD eigenvalue, including empty dimensions. -/
theorem eigenvalue_le_trace (S : Matrix κ κ ℝ) (hS : S.PosSemidef) (i : κ) :
    hS.isHermitian.eigenvalues i ≤ S.trace := by
  rw [hS.isHermitian.trace_eq_sum_eigenvalues]
  exact Finset.single_le_sum (fun j _ => hS.eigenvalues_nonneg j) (Finset.mem_univ i)

/-- Self-adjointness moves the matrix to a unit eigenvector. -/
theorem inner_eigenvector_action (S : Matrix κ κ ℝ) (hS : S.IsHermitian)
    (i : κ) (x : EuclideanSpace ℝ κ) :
    ⟪hS.eigenvectorBasis i, matrixCLM S x⟫ =
      hS.eigenvalues i * ⟪hS.eigenvectorBasis i, x⟫ := by
  have ht : S.transpose = S := by simpa only [Matrix.conjTranspose_eq_transpose_of_trivial] using hS.eq
  rw [← ContinuousLinearMap.adjoint_inner_left, matrixCLM_adjoint, ht, eigenvector_action]
  simp only [real_inner_smul_left]

/-- Sharp Richardson contraction from a certified spectral interval, in Euclidean square norm. -/
theorem richardson_vector_sq_contract (S : Matrix κ κ ℝ) (hS : S.IsHermitian)
    (σ Λ : ℝ) (hΛ : 0 < Λ)
    (hlo : ∀ i, σ ≤ hS.eigenvalues i) (hhi : ∀ i, hS.eigenvalues i ≤ Λ)
    (x : EuclideanSpace ℝ κ) :
    ‖x - Λ⁻¹ • matrixCLM S x‖^2 ≤ (1-σ/Λ)^2 * ‖x‖^2 := by
  let b := hS.eigenvectorBasis
  rw [← b.sum_sq_inner_right (x - Λ⁻¹ • matrixCLM S x), ← b.sum_sq_inner_right x,
    Finset.mul_sum]
  apply Finset.sum_le_sum
  intro i _
  have hl : 0 ≤ 1 - hS.eigenvalues i / Λ := by
    have := (div_le_one hΛ).mpr (hhi i)
    linarith
  have hu : 1 - hS.eigenvalues i / Λ ≤ 1 - σ/Λ := by
    have := (div_le_div_iff_of_pos_right hΛ).mpr (hlo i)
    linarith
  have hsquare : (1 - hS.eigenvalues i / Λ)^2 ≤ (1-σ/Λ)^2 :=
    pow_le_pow_left₀ hl hu 2
  have he : ⟪b i, x - Λ⁻¹ • matrixCLM S x⟫ =
      (1-hS.eigenvalues i/Λ)*⟪b i,x⟫ := by
    dsimp [b]
    rw [inner_sub_right, real_inner_smul_right, inner_eigenvector_action]
    ring
  rw [he, mul_pow]
  exact mul_le_mul_of_nonneg_right hsquare (sq_nonneg _)
end Komorebi.GainSolver
