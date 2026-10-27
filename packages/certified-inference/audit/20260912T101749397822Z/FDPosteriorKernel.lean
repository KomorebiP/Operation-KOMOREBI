import Komorebi.FDGaussianKernel
import Komorebi.FDJointCovPSD

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix ProbabilityTheory MeasureTheory

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- The candidate posterior uses the covariance already derived from Joseph form. -/
def fdPosteriorKernel (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) :
    Kernel (EuclideanSpace ℝ κ) (EuclideanSpace ℝ ι) :=
  gaussianAffineKernel (gainMatrix H P R)
    (m - matrixCLM (gainMatrix H P R) (matrixCLM H m)) (posteriorCovMatrix H P R)

instance fdPosteriorKernel_isMarkov (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) : IsMarkovKernel (fdPosteriorKernel H m P R) := by
  unfold fdPosteriorKernel
  infer_instance

/-- The candidate mean is exactly the Kalman innovation update. -/
theorem fdPosteriorKernel_apply (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι)
    (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) (y : EuclideanSpace ℝ κ) :
    fdPosteriorKernel H m P R y =
      multivariateGaussian (m + matrixCLM (gainMatrix H P R) (y - matrixCLM H m))
        (posteriorCovMatrix H P R) := by
  rw [fdPosteriorKernel, gaussianAffineKernel_apply, map_sub]
  congr 1
  abel

end Komorebi.FiniteDimensionalGaussianKalman
