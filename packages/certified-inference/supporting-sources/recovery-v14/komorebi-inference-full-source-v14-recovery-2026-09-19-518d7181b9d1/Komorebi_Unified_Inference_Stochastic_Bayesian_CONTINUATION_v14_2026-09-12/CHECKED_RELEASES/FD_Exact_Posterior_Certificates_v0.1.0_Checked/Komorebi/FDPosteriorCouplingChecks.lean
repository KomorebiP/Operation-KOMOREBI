import Komorebi.FDResidualEnergyCertificate
import Komorebi.FDPosteriorFactorCoupling
import Komorebi.QuadraticTransportSemantics

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open MeasureTheory ProbabilityTheory Matrix Komorebi.QuadraticTransport
open scoped ENNReal NNReal

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

omit [DecidableEq ι] in
/-- Regression: an exact gain has zero equation residual. -/
theorem exact_gain_residual_zero (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ)
    (R : Matrix κ κ ℝ) (hP : P.PosSemidef) (hR : R.PosDef) :
    gainResidual H P R (gainMatrix H P R) = 0 := by
  simp only [gainResidual, gain_mul_innovation H P R hP hR, sub_self]

/-- Regression: no spurious distance when the solve is exact. -/
theorem exact_gain_wasserstein2_zero (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (y : EuclideanSpace ℝ κ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    wasserstein2 (fdPosteriorKernel H m P R y)
      (gainPosteriorLaw H m P R (gainMatrix H P R) y) = 0 := by
  rw [gainPosteriorLaw_exact H m P R y hP hR, wasserstein2_self]

omit [DecidableEq ι] [DecidableEq κ] in
/-- Regression: the deterministic-prior case does not require an inverse prior. -/
theorem zero_prior_zero_gain_residual (H : Matrix κ ι ℝ) (R : Matrix κ κ ℝ) :
    gainResidual H (0 : Matrix ι ι ℝ) R (0 : Matrix ι κ ℝ) = 0 := by
  simp only [gainResidual, Matrix.zero_mul, sub_self]

omit [DecidableEq ι] [DecidableEq κ] in
/-- Regression: zero observation has zero residual at zero gain. -/
theorem zero_observation_zero_gain_residual (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) :
    gainResidual (0 : Matrix κ ι ℝ) P R (0 : Matrix ι κ ℝ) = 0 := by
  simp only [gainResidual, Matrix.transpose_zero, Matrix.mul_zero, Matrix.zero_mul, sub_self]

omit [DecidableEq κ] in
/-- Regression: a zero gain preserves the prior covariance exactly. -/
theorem zero_gain_joseph (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) :
    gainJoseph H P R (0 : Matrix ι κ ℝ) = P := by
  simp only [gainJoseph, Matrix.zero_mul, sub_zero, Matrix.transpose_one,
    Matrix.one_mul, Matrix.mul_one, add_zero]

/-- Regression: a zero residual gives a zero distribution error for every observation. -/
theorem residual_zero_wasserstein2_zero (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (hP : P.PosSemidef) (hR : R.PosDef)
    (hF : gainResidual H P R B = 0) :
    wasserstein2 (fdPosteriorKernel H m P R y) (gainPosteriorLaw H m P R B y) = 0 := by
  rw [gainPosteriorLaw_eq_of_residual_zero H m P R B y hP hR hF, wasserstein2_self]

omit [DecidableEq κ] in
/-- The residual majorant is nonnegative on its declared conditioning domain. -/
theorem gainResidualEnergyBudget_nonneg (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (B : Matrix ι κ ℝ)
    (y : EuclideanSpace ℝ κ) (σ : ℝ) (hσ : 0 < σ) :
    0 ≤ gainResidualEnergyBudget H m P R B y σ := by
  unfold gainResidualEnergyBudget frobeniusSq
  positivity

end Komorebi.FiniteDimensionalGaussianKalman
