import Komorebi.FDJointCovPSD
import Mathlib.Probability.Distributions.Gaussian.Multivariate

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman

open Matrix ProbabilityTheory MeasureTheory
open scoped ProbabilityTheory

variable {ι κ : Type*} [Fintype ι] [Fintype κ]

/-- At any common joint mean, the forward and reverse Gaussian parameterizations
    define exactly the same multivariate Gaussian law. -/
theorem multivariateGaussian_reverseJointCov_eq_forwardJointCov
    [DecidableEq ι] [DecidableEq κ]
    (μ : EuclideanSpace ℝ (κ ⊕ ι))
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ)
    (hP : P.PosSemidef) (hR : R.PosDef) :
    multivariateGaussian μ (reverseJointCov H P R) =
      multivariateGaussian μ (forwardJointCov H P R) := by
  rw [reverseJointCov_eq_forwardJointCov H P R hP hR]

end Komorebi.FiniteDimensionalGaussianKalman
