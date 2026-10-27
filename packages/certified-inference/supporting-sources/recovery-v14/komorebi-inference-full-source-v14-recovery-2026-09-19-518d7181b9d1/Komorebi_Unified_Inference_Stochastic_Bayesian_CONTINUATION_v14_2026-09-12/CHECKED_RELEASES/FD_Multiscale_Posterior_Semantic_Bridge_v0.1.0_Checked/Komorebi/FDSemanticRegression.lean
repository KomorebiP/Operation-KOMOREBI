import Komorebi.FDPosteriorCertificate
import Komorebi.FDConditioningChecks

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman
open Matrix ProbabilityTheory MeasureTheory Komorebi.BayesianPosteriorPerturb

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- Centering regression: arbitrary deterministic mean contributes no covariance. -/
theorem centeredCovOp_deterministic (m : EuclideanSpace ℝ ι) :
    centeredCovOp (multivariateGaussian m (0 : Matrix ι ι ℝ)) = 0 := by
  rw [centeredCovOp_multivariateGaussian m 0 (Matrix.PosSemidef.zero), matrixCLM_zero]

namespace GaussianModel

/-- Same model, different data: the covariance discrepancy is exactly zero. -/
theorem posteriorCovDiscrepancy_self (M : GaussianModel ι κ) (y y0 : EuclideanSpace ℝ κ) :
    M.posteriorCovDiscrepancy M y y0 = 0 := by
  simp only [posteriorCovDiscrepancy, posterior_covariance_matrix, sub_self]

/-- Identical models have an exactly zero covariance budget. -/
theorem covarianceErrorBudget_self (M : GaussianModel ι κ) : M.covarianceErrorBudget M = 0 := by
  simp [covarianceErrorBudget, closedErrorBudget, gainErrorBudget,
    posteriorCovPerturbBudget, closedLoopPerturbBudget, gainPerturbBudget, innovationPerturbBudget]

/-- Identical models at identical data have an exactly zero mean budget. -/
theorem meanErrorBudget_self (M : GaussianModel ι κ) (y : EuclideanSpace ℝ κ) :
    M.meanErrorBudget M y y = 0 := by
  simp [meanErrorBudget, gainErrorBudget, gainPerturbBudget, innovationPerturbBudget]

/-- A deterministic prior stays zero-covariance even when its mean is nonzero. -/
theorem posterior_covariance_zero_prior (M : GaussianModel ι κ)
    (h : M.priorCov = 0) (y : EuclideanSpace ℝ κ) :
    centeredCovOp (M.posteriorLaw y) = 0 := by
  rw [posteriorLaw, h, fdPosteriorKernel_zero_prior_covariance, centeredCovOp_deterministic]

/-- No observation information leaves the actual covariance equal to the prior covariance. -/
theorem posterior_covariance_zero_observation (M : GaussianModel ι κ)
    (h : M.observation = 0) (y : EuclideanSpace ℝ κ) :
    centeredCovOp (M.posteriorLaw y) = M.priorOp := by
  rw [posteriorLaw, h, fdPosteriorKernel_zero_observation]
  exact centeredCovOp_multivariateGaussian M.mean M.priorCov M.prior_valid

end GaussianModel
end Komorebi.FiniteDimensionalGaussianKalman
