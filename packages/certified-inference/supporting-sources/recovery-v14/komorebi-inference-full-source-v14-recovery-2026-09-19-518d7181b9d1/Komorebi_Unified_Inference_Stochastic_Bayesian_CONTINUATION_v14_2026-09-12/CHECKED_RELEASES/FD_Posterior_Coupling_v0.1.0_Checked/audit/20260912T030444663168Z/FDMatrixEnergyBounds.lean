import Komorebi.FDMatrixOperatorCompat
import Mathlib.Algebra.Order.BigOperators.Ring.Finset

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix
open scoped RealInnerProductSpace

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- Squared Frobenius norm, with explicit finite-coordinate normalization. -/
def frobeniusSq (A : Matrix ι κ ℝ) : ℝ := ∑ i, ∑ j, (A i j)^2

omit [DecidableEq ι] [DecidableEq κ] in
theorem frobeniusSq_nonneg (A : Matrix ι κ ℝ) : 0 ≤ frobeniusSq A := by
  exact Finset.sum_nonneg (fun i _ => Finset.sum_nonneg (fun j _ => sq_nonneg (A i j)))

omit [DecidableEq ι] [DecidableEq κ] in
/-- The factor energy equals its covariance trace. -/
theorem trace_mul_transpose_eq_frobeniusSq (A : Matrix ι κ ℝ) :
    (A*A.transpose).trace = frobeniusSq A := by
  simp only [Matrix.trace, Matrix.mul_apply, Matrix.transpose_apply, frobeniusSq, pow_two]

omit [DecidableEq ι] in
/-- Euclidean matrix action is bounded by its explicit factor energy. -/
theorem matrixCLM_apply_sq_le_frobeniusSq (A : Matrix ι κ ℝ) (v : EuclideanSpace ℝ κ) :
    ‖matrixCLM A v‖^2 ≤ frobeniusSq A * ‖v‖^2 := by
  simp only [matrixCLM_apply, EuclideanSpace.real_norm_sq_eq, WithLp.ofLp_toLp]
  calc
    ∑ i, ((A *ᵥ v) i)^2 ≤ ∑ i, ((∑ j, (A i j)^2)*(∑ j, (v j)^2)) := by
      apply Finset.sum_le_sum
      intro i _
      exact Finset.sum_mul_sq_le_sq_mul_sq Finset.univ (A i) (fun j => v j)
    _ = frobeniusSq A * ∑ j, (v j)^2 := by
      rw [← Finset.sum_mul]
      rfl

omit [DecidableEq ι] in
/-- Trace of an image covariance as rowwise quadratic forms. -/
theorem trace_image_eq_sum_inner (F : Matrix ι κ ℝ) (Q : Matrix κ κ ℝ) :
    (F*Q*F.transpose).trace =
      ∑ i, ⟪WithLp.toLp 2 (F i), matrixCLM Q (WithLp.toLp 2 (F i))⟫ := by
  simp only [Matrix.trace, matrixCLM_apply, EuclideanSpace.inner_eq_star_dotProduct,
    star_trivial, WithLp.ofLp_toLp, Matrix.dotProduct_mulVec]
  rfl

omit [DecidableEq ι] in
/-- A certified Euclidean operator-norm bound controls the quadratic trace. -/
theorem trace_image_le_norm_mul_frobeniusSq (F : Matrix ι κ ℝ) (Q : Matrix κ κ ℝ)
    (c : ℝ) (hQ : ‖matrixCLM Q‖ ≤ c) :
    (F*Q*F.transpose).trace ≤ c * frobeniusSq F := by
  rw [trace_image_eq_sum_inner]
  calc
    _ ≤ ∑ i, c * ‖(WithLp.toLp 2 (F i) : EuclideanSpace ℝ κ)‖^2 := by
      apply Finset.sum_le_sum
      intro i _
      let x : EuclideanSpace ℝ κ := WithLp.toLp 2 (F i)
      calc
        ⟪x, matrixCLM Q x⟫ ≤ ‖x‖ * ‖matrixCLM Q x‖ := real_inner_le_norm x _
        _ ≤ ‖x‖ * (c*‖x‖) := mul_le_mul_of_nonneg_left
          ((matrixCLM Q).le_opNorm x |>.trans (mul_le_mul_of_nonneg_right hQ (norm_nonneg x)))
          (norm_nonneg x)
        _ = c*‖x‖^2 := by ring
    _ = c * frobeniusSq F := by
      simp only [EuclideanSpace.real_norm_sq_eq, WithLp.ofLp_toLp]
      rw [← Finset.mul_sum]
      rfl

end Komorebi.FiniteDimensionalGaussianKalman
