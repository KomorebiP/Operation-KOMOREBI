import Komorebi.FDMatrixOperatorCompat
import Komorebi.FDPosteriorCovPSD
import Komorebi.PosteriorRefinement

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix Komorebi.BayesianPosteriorPerturb

variable {ι κ : Type*} [Fintype ι] [Fintype κ]
variable [DecidableEq ι] [DecidableEq κ]

/-- Matrix innovation and the coordinate-free innovation are the same operator. -/
theorem matrixCLM_innovation
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) :
    matrixCLM (innovationMatrix H P R) =
      kalmanInnovationOp (matrixCLM H) (matrixCLM P) (matrixCLM R) := by
  simp only [innovationMatrix, kalmanInnovationOp, matrixCLM_add, matrixCLM_mul,
    matrixCLM_adjoint, ContinuousLinearMap.comp_assoc]

/-- Matrix Kalman gain and the coordinate-free gain are the same operator. -/
theorem matrixCLM_gain
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) :
    matrixCLM (gainMatrix H P R) =
      kalmanGainOp (matrixCLM P) (matrixCLM H)
        (matrixCLM (innovationMatrix H P R)⁻¹) := by
  simp only [gainMatrix, kalmanGainOp, matrixCLM_mul, matrixCLM_adjoint,
    ContinuousLinearMap.comp_assoc]

/-- The inverse hypotheses of the perturbation theorem follow from model validity. -/
theorem matrixCLM_innovation_left_inverse
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    (matrixCLM (innovationMatrix H P R)⁻¹).comp
        (kalmanInnovationOp (matrixCLM H) (matrixCLM P) (matrixCLM R)) =
      ContinuousLinearMap.id ℝ (EuclideanSpace ℝ κ) := by
  rw [← matrixCLM_innovation, ← matrixCLM_mul, innovation_inv_mul H P R hP hR,
    matrixCLM_one]

/-- The second model's required right inverse is derived, not postulated. -/
theorem matrixCLM_innovation_right_inverse
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    (kalmanInnovationOp (matrixCLM H) (matrixCLM P) (matrixCLM R)).comp
        (matrixCLM (innovationMatrix H P R)⁻¹) =
      ContinuousLinearMap.id ℝ (EuclideanSpace ℝ κ) := by
  rw [← matrixCLM_innovation, ← matrixCLM_mul, innovation_mul_inv H P R hP hR,
    matrixCLM_one]

/-- The closed-loop matrix is the existing closed-loop operator. -/
theorem matrixCLM_closedLoop (K : Matrix ι κ ℝ) (H : Matrix κ ι ℝ) :
    matrixCLM (1 - K * H) = kalmanClosedLoop (matrixCLM K) (matrixCLM H) := by
  simp only [matrixCLM_sub, matrixCLM_one, matrixCLM_mul, kalmanClosedLoop]

/-- The Joseph matrix and the existing Joseph operator agree exactly. -/
theorem matrixCLM_joseph
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) :
    matrixCLM (josephCovMatrix H P R) =
      josephPosteriorCov (matrixCLM (gainMatrix H P R)) (matrixCLM H)
        (matrixCLM P) (matrixCLM R) := by
  simp only [josephCovMatrix, josephPosteriorCov, kalmanClosedLoop,
    matrixCLM_add, matrixCLM_mul, ← matrixCLM_adjoint,
    matrixCLM_sub, matrixCLM_one, ContinuousLinearMap.comp_assoc]

/-- The proved conditional covariance matrix is the existing Joseph covariance operator. -/
theorem matrixCLM_posteriorCov
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    matrixCLM (posteriorCovMatrix H P R) =
      josephPosteriorCov (matrixCLM (gainMatrix H P R)) (matrixCLM H)
        (matrixCLM P) (matrixCLM R) := by
  rw [← josephCovMatrix_eq_posteriorCovMatrix H P R hP hR, matrixCLM_joseph]

end Komorebi.FiniteDimensionalGaussianKalman
