import Komorebi.FDInexactGainCoupling
import Komorebi.FDInnovationConditioning
import Komorebi.QuadraticTransportBounds

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open MeasureTheory ProbabilityTheory Matrix Komorebi.QuadraticTransport
open scoped ENNReal NNReal

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

omit [DecidableEq ι] in
/-- The exact quadratic residual expression admits an inverse-free energy majorant
once a valid bound on the auxiliary operator has been supplied. -/
theorem quadratic_residual_cost_le_energy
    (F : Matrix ι κ ℝ) (Q : Matrix κ κ ℝ) (v : EuclideanSpace ℝ κ)
    (c : ℝ) (hQ : ‖matrixCLM Q‖ ≤ c) :
    ‖matrixCLM (F*Q) v‖^2 + (F*Q*F.transpose).trace ≤
      frobeniusSq F * (c+c^2*‖v‖^2) := by
  have hv : ‖matrixCLM Q v‖ ≤ c*‖v‖ :=
    ((matrixCLM Q).le_opNorm v).trans (mul_le_mul_of_nonneg_right hQ (norm_nonneg _))
  have hm : ‖matrixCLM (F*Q) v‖^2 ≤ frobeniusSq F*(c*‖v‖)^2 := by
    rw [matrixCLM_mul, ContinuousLinearMap.comp_apply]
    exact (matrixCLM_apply_sq_le_frobeniusSq F (matrixCLM Q v)).trans
      (mul_le_mul_of_nonneg_left (pow_le_pow_left₀ (norm_nonneg _) hv 2) (frobeniusSq_nonneg F))
  calc
    _ ≤ frobeniusSq F*(c*‖v‖)^2 + c*frobeniusSq F :=
      add_le_add hm (trace_image_le_norm_mul_frobeniusSq F Q c hQ)
    _ = _ := by ring

/-- Explicit residual budget. Its inputs contain no exact gain or inverse innovation. -/
def gainResidualEnergyBudget (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (σ : ℝ) : ℝ :=
  frobeniusSq (gainResidual H P R B) * (σ⁻¹+(σ⁻¹)^2*‖y-matrixCLM H m‖^2)

/-- A noise floor and an approximate gain's computable residual bound actual posterior error. -/
theorem posterior_wasserstein2Sq_le_residual_energy
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (hP : P.PosSemidef) (hR : R.PosDef)
    (σ : ℝ) (hσ : 0 < σ) (hfloor : QuadraticLowerBound R σ) :
    wasserstein2Sq (fdPosteriorKernel H m P R y) (gainPosteriorLaw H m P R B y) ≤
      ENNReal.ofReal (gainResidualEnergyBudget H m P R B y σ) := by
  apply (posterior_wasserstein2Sq_le_gain_residual H m P R B y hP hR).trans
  apply ENNReal.ofReal_le_ofReal
  exact quadratic_residual_cost_le_energy _ _ _ (σ⁻¹)
    (innovation_inverse_norm_le H P R hP hR σ hσ hfloor)

/-- Residual-only stopping rule, in squared form to avoid square-root evaluation.
This proves a mathematical stopping certificate, not verified floating-point computation. -/
theorem posterior_wasserstein2_le_of_residual_tolerance
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (hP : P.PosSemidef) (hR : R.PosDef)
    (σ ε : ℝ) (hσ : 0 < σ) (hε : 0 ≤ ε) (hfloor : QuadraticLowerBound R σ)
    (hstop : frobeniusSq (gainResidual H P R B)*(σ+‖y-matrixCLM H m‖^2) ≤ ε^2*σ^2) :
    wasserstein2 (fdPosteriorKernel H m P R y) (gainPosteriorLaw H m P R B y) ≤
      ENNReal.ofReal ε := by
  apply wasserstein2_le_of_sq_le _ _ ε hε
  apply (posterior_wasserstein2Sq_le_residual_energy H m P R B y hP hR σ hσ hfloor).trans
  apply ENNReal.ofReal_le_ofReal
  have heq : gainResidualEnergyBudget H m P R B y σ =
      frobeniusSq (gainResidual H P R B)*(σ+‖y-matrixCLM H m‖^2)/σ^2 := by
    unfold gainResidualEnergyBudget
    field_simp
  rw [heq]
  exact (div_le_iff₀ (sq_pos_of_pos hσ)).mpr hstop

end Komorebi.FiniteDimensionalGaussianKalman
