import Komorebi.FDMatrixEnergyBounds
import Komorebi.FDInnovationIdentities

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix
open scoped RealInnerProductSpace

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- A lower quadratic bound in the actual Euclidean geometry. -/
def QuadraticLowerBound (S : Matrix κ κ ℝ) (σ : ℝ) : Prop :=
  ∀ x : EuclideanSpace ℝ κ, σ*‖x‖^2 ≤ ⟪x, matrixCLM S x⟫

/-- Matrix semidefiniteness has the expected Euclidean quadratic interpretation. -/
theorem matrixCLM_inner_nonneg (S : Matrix κ κ ℝ) (hS : S.PosSemidef)
    (x : EuclideanSpace ℝ κ) : 0 ≤ ⟪x, matrixCLM S x⟫ := by
  simp only [matrixCLM_apply, EuclideanSpace.inner_eq_star_dotProduct, star_trivial]
  rw [dotProduct_comm]
  simpa only [star_trivial] using hS.dotProduct_mulVec_nonneg (fun i => x i)

/-- Coercivity and an actual right inverse give an explicit inverse norm bound. -/
theorem inverse_norm_le_of_quadraticLowerBound (S Q : Matrix κ κ ℝ)
    (σ : ℝ) (hσ : 0 < σ) (hSQ : S*Q=1) (hS : QuadraticLowerBound S σ) :
    ‖matrixCLM Q‖ ≤ σ⁻¹ := by
  apply (matrixCLM Q).opNorm_le_bound (inv_nonneg.mpr hσ.le)
  intro v
  have hsx : matrixCLM S (matrixCLM Q v) = v := by
    change ((matrixCLM S).comp (matrixCLM Q)) v = _
    rw [← matrixCLM_mul, hSQ, matrixCLM_one]
    rfl
  have hx := hS (matrixCLM Q v)
  rw [hsx] at hx
  have hi := real_inner_le_norm (matrixCLM Q v) v
  by_cases hz : ‖matrixCLM Q v‖ = 0
  · rw [hz]
    positivity
  have hp : 0 < ‖matrixCLM Q v‖ := lt_of_le_of_ne (norm_nonneg _) (Ne.symm hz)
  have hlin : σ*‖matrixCLM Q v‖ ≤ ‖v‖ := by
    apply (mul_le_mul_iff_right₀ hp).mp
    nlinarith
  have hdiv : ‖matrixCLM Q v‖ ≤ ‖v‖/σ := (le_div_iff₀ hσ).mpr (by nlinarith)
  simpa only [div_eq_mul_inv, mul_comm] using hdiv

/-- A noise covariance floor is inherited by the innovation, including singular priors. -/
theorem innovation_quadraticLowerBound (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ)
    (R : Matrix κ κ ℝ) (hP : P.PosSemidef) (σ : ℝ) (hR : QuadraticLowerBound R σ) :
    QuadraticLowerBound (innovationMatrix H P R) σ := by
  intro x
  have hp := matrixCLM_inner_nonneg (H*P*H.transpose) (imageCov_posSemidef H P hP) x
  have hr := hR x
  simp only [innovationMatrix, matrixCLM_add, _root_.add_apply, inner_add_right]
  linarith

/-- The displayed noise floor certifies the true innovation inverse norm. -/
theorem innovation_inverse_norm_le (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ)
    (R : Matrix κ κ ℝ) (hP : P.PosSemidef) (hR : R.PosDef)
    (σ : ℝ) (hσ : 0 < σ) (hfloor : QuadraticLowerBound R σ) :
    ‖matrixCLM (innovationMatrix H P R)⁻¹‖ ≤ σ⁻¹ := by
  exact inverse_norm_le_of_quadraticLowerBound _ _ σ hσ
    (innovation_mul_inv H P R hP hR) (innovation_quadraticLowerBound H P R hP σ hfloor)

end Komorebi.FiniteDimensionalGaussianKalman
