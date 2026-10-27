import Komorebi.FDPosteriorModel

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman.GaussianModel
open MeasureTheory Komorebi.BayesianPosteriorPerturb

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- The inherited gain budget evaluated on valid finite-dimensional models. -/
def gainErrorBudget (M M0 : GaussianModel ι κ) : ℝ :=
  gainPerturbBudget M.observationOp M0.observationOp M.priorOp M0.priorOp
    M.noiseOp M0.noiseOp M.inverseInnovationOp M0.inverseInnovationOp

def closedErrorBudget (M M0 : GaussianModel ι κ) : ℝ :=
  closedLoopPerturbBudget M0.gainOp M.observationOp M0.observationOp (M.gainErrorBudget M0)

/-- The inherited residual budget, with no assumed inverse equations. -/
def covarianceErrorBudget (M M0 : GaussianModel ι κ) : ℝ :=
  posteriorCovPerturbBudget M.gainOp M0.gainOp M.observationOp M0.observationOp
    M.priorOp M0.priorOp M.noiseOp M0.noiseOp
    (M.gainErrorBudget M0) (M.closedErrorBudget M0)

/-- Difference of the actual centered covariance operators of two posterior laws. -/
def posteriorCovDiscrepancy (M M0 : GaussianModel ι κ)
    (y y0 : EuclideanSpace ℝ κ) : EuclideanSpace ℝ ι →L[ℝ] EuclideanSpace ℝ ι :=
  centeredCovOp (M.posteriorLaw y) - centeredCovOp (M0.posteriorLaw y0)

/-- The abstract error operator is exactly the actual posterior covariance discrepancy. -/
theorem posteriorCovDiscrepancy_eq_operator (M M0 : GaussianModel ι κ)
    (y y0 : EuclideanSpace ℝ κ) :
    M.posteriorCovDiscrepancy M0 y y0 =
      posteriorCovErrorOp M.gainOp M0.gainOp M.observationOp M0.observationOp
        M.priorOp M0.priorOp M.noiseOp M0.noiseOp := by
  unfold posteriorCovDiscrepancy posteriorCovErrorOp
  rw [posterior_covariance_operator, posterior_covariance_operator]

/-- The abstract gain bound applies with inverses derived from covariance validity. -/
theorem gain_error_norm_le_budget (M M0 : GaussianModel ι κ) :
    ‖M.gainOp - M0.gainOp‖ ≤ M.gainErrorBudget M0 := by
  simpa only [gainOp_eq_operator, gainErrorBudget] using
    kalmanGainOp_sub_norm_le_residual_budget
      M.observationOp M0.observationOp M.priorOp M0.priorOp M.noiseOp M0.noiseOp
      M.inverseInnovationOp M0.inverseInnovationOp
      M.innovation_left_inverse M0.innovation_right_inverse

/-- The closed-loop perturbation bound for valid finite-dimensional models. -/
theorem closed_error_norm_le_budget (M M0 : GaussianModel ι κ) :
    ‖kalmanClosedLoop M.gainOp M.observationOp -
        kalmanClosedLoop M0.gainOp M0.observationOp‖ ≤ M.closedErrorBudget M0 := by
  simpa only [closedErrorBudget, gainErrorBudget, gainOp_eq_operator] using
    kalmanClosedLoop_sub_norm_le_residual_budget
      M.observationOp M0.observationOp M.priorOp M0.priorOp M.noiseOp M0.noiseOp
      M.inverseInnovationOp M0.inverseInnovationOp
      M.innovation_left_inverse M0.innovation_right_inverse

/-- End-to-end semantic covariance certificate for genuine Bayesian posterior versions.
Both priors may be singular. Observations may differ. Norms are Euclidean operator norms. -/
theorem posterior_covariance_norm_le_budget (M M0 : GaussianModel ι κ)
    (y y0 : EuclideanSpace ℝ κ) :
    ‖M.posteriorCovDiscrepancy M0 y y0‖ ≤ M.covarianceErrorBudget M0 := by
  rw [posteriorCovDiscrepancy_eq_operator]
  simpa only [posteriorCovErrorOp, covarianceErrorBudget, closedErrorBudget,
    gainErrorBudget, gainOp_eq_operator] using
    josephPosteriorCov_sub_norm_le_residual_budget
      M.observationOp M0.observationOp M.priorOp M0.priorOp M.noiseOp M0.noiseOp
      M.inverseInnovationOp M0.inverseInnovationOp
      M.innovation_left_inverse M0.innovation_right_inverse

end Komorebi.FiniteDimensionalGaussianKalman.GaussianModel
