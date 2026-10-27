import Komorebi.FDPosteriorBudgets

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman.GaussianModel
open MeasureTheory Komorebi.BayesianPosteriorPerturb

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- The pathwise mean certificate retains the actual innovation magnitude. -/
def meanErrorBudget (M M0 : GaussianModel ι κ) (y y0 : EuclideanSpace ℝ κ) : ℝ :=
  ‖M.mean - M0.mean‖ +
  M.gainErrorBudget M0 * ‖y - M.observationOp M.mean‖ +
  ‖M0.gainOp‖ * (‖y-y0‖ + ‖M.observationOp - M0.observationOp‖ * ‖M.mean‖ +
    ‖M0.observationOp‖ * ‖M.mean - M0.mean‖)

/-- The existing mean perturbation budget bounds actual posterior expectations. -/
theorem posterior_mean_norm_le_budget (M M0 : GaussianModel ι κ)
    (y y0 : EuclideanSpace ℝ κ) :
    ‖(∫ x, x ∂M.posteriorLaw y) - (∫ x, x ∂M0.posteriorLaw y0)‖ ≤
      M.meanErrorBudget M0 y y0 := by
  rw [posterior_expectation, posterior_expectation]
  simpa only [meanErrorBudget, gainErrorBudget, gainOp_eq_operator] using
    kalmanPosteriorMean_sub_norm_le_residual_budget
      M.observationOp M0.observationOp M.priorOp M0.priorOp M.noiseOp M0.noiseOp
      M.inverseInnovationOp M0.inverseInnovationOp M.mean M0.mean y y0
      M.innovation_left_inverse M0.innovation_right_inverse

/-- Both certified moments of explicit posterior versions at arbitrary observations. -/
theorem posterior_moment_certificates (M M0 : GaussianModel ι κ)
    (y y0 : EuclideanSpace ℝ κ) :
    ‖(∫ x, x ∂M.posteriorLaw y) - (∫ x, x ∂M0.posteriorLaw y0)‖ ≤
        M.meanErrorBudget M0 y y0 ∧
    ‖centeredCovOp (M.posteriorLaw y) - centeredCovOp (M0.posteriorLaw y0)‖ ≤
        M.covarianceErrorBudget M0 := by
  exact ⟨M.posterior_mean_norm_le_budget M0 y y0,
    M.posterior_covariance_norm_le_budget M0 y y0⟩

/-- Canonical versions inherit both certificates, under their respective evidence measures.
No common exceptional set or cross-model absolute continuity is assumed. -/
theorem canonical_moment_certificates_ae (M M0 : GaussianModel ι κ) :
    ∀ᵐ y ∂M.evidenceLaw, ∀ᵐ y0 ∂M0.evidenceLaw,
      ‖(∫ x, x ∂M.canonicalKernel y) - (∫ x, x ∂M0.canonicalKernel y0)‖ ≤
          M.meanErrorBudget M0 y y0 ∧
      ‖centeredCovOp (M.canonicalKernel y) - centeredCovOp (M0.canonicalKernel y0)‖ ≤
          M.covarianceErrorBudget M0 := by
  filter_upwards [M.posteriorLaw_ae_eq_canonical] with y hy
  filter_upwards [M0.posteriorLaw_ae_eq_canonical] with y0 hy0
  rw [← hy, ← hy0]
  exact M.posterior_moment_certificates M0 y y0

end Komorebi.FiniteDimensionalGaussianKalman.GaussianModel
