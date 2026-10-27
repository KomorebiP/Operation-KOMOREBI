import Komorebi.FDResidualPacketCertificate

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix Komorebi.QuadraticTransport
open scoped ENNReal

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- Both residual energy and the observed innovation may be replaced by certified upper bounds. -/
theorem posterior_wasserstein2Sq_le_energy_majorants
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (hP : P.PosSemidef) (hR : R.PosDef)
    (σ : ℝ) (hσ : 0 < σ) (hfloor : QuadraticLowerBound R σ)
    (U V : ℝ) (hU : frobeniusSq (gainResidual H P R B) ≤ U)
    (hV : ‖y-matrixCLM H m‖^2 ≤ V) :
    wasserstein2Sq (fdPosteriorKernel H m P R y) (gainPosteriorLaw H m P R B y) ≤
      ENNReal.ofReal (U*(σ+V)/σ^2) := by
  apply (posterior_wasserstein2Sq_le_residual_energy H m P R B y hP hR σ hσ hfloor).trans
  apply ENNReal.ofReal_le_ofReal
  have heq : gainResidualEnergyBudget H m P R B y σ =
      frobeniusSq (gainResidual H P R B)*(σ+‖y-matrixCLM H m‖^2)/σ^2 := by
    unfold gainResidualEnergyBudget
    field_simp
  rw [heq]
  exact div_le_div_of_nonneg_right
    (mul_le_mul hU (add_le_add_left hV σ)
      (add_nonneg hσ.le (sq_nonneg _)) ((frobeniusSq_nonneg _).trans hU)) (sq_nonneg σ)

end Komorebi.FiniteDimensionalGaussianKalman
