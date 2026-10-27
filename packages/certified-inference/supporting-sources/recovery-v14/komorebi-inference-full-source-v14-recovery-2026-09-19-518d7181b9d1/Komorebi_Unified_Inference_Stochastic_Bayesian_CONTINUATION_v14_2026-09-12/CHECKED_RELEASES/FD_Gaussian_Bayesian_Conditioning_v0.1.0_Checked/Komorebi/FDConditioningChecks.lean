import Komorebi.FDGaussianConditioning

noncomputable section
set_option autoImplicit false
namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix ProbabilityTheory MeasureTheory

/-- Regression: zero observation operator leaves the explicit posterior unchanged. -/
theorem fdPosteriorKernel_zero_observation
    {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]
    (m : EuclideanSpace ℝ ι) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (y : EuclideanSpace ℝ κ) :
    fdPosteriorKernel (0 : Matrix κ ι ℝ) m P R y = multivariateGaussian m P := by
  rw [fdPosteriorKernel_apply]
  simp [gainMatrix, posteriorCovMatrix]

/-- Regression: a deterministic Gaussian prior remains deterministic after observation. -/
theorem fdPosteriorKernel_zero_prior_covariance
    {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]
    (H : Matrix κ ι ℝ) (m : EuclideanSpace ℝ ι) (R : Matrix κ κ ℝ)
    (y : EuclideanSpace ℝ κ) :
    fdPosteriorKernel H m 0 R y = multivariateGaussian m 0 := by
  rw [fdPosteriorKernel_apply]
  simp [gainMatrix, posteriorCovMatrix]

end Komorebi.FiniteDimensionalGaussianKalman
