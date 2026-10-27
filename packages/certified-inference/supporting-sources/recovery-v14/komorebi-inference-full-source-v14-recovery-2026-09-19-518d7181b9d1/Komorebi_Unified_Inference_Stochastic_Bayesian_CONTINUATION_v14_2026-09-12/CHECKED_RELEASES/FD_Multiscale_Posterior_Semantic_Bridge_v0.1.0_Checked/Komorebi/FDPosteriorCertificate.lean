import Komorebi.FDPosteriorRefinement
import Komorebi.FDPosteriorExactResiduals

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman.GaussianModel
open MeasureTheory Komorebi.AbstractProjectorRefinement

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]
variable {cLane fLane : Type*} [Fintype cLane] [Fintype fLane] [DecidableEq cLane]

/-- A single end-to-end semantic multiscale certificate. Model validity supplies the
Gaussian posterior law and inverse equations. The declared projector hypotheses supply
exact refinement and the quantitative block bound. No posterior error is assumed. -/
theorem multiscale_posterior_certificate (M M0 : GaussianModel ι κ)
    (C : ProjectorFamily (EuclideanSpace ℝ ι) cLane)
    (F : ProjectorFamily (EuclideanSpace ℝ ι) fLane)
    (ρ : fLane → cLane) (hRef : Refines C F ρ) (hC : ∀ a, ‖C.proj a‖ ≤ 1)
    (y y0 : EuclideanSpace ℝ κ) (a b : cLane) :
    ‖(∫ x, x ∂M.posteriorLaw y) - (∫ x, x ∂M0.posteriorLaw y0)‖ ≤
        M.meanErrorBudget M0 y y0 ∧
    ‖M.posteriorCovDiscrepancy M0 y y0‖ ≤ M.covarianceErrorBudget M0 ∧
    opBlock C (M.posteriorCovDiscrepancy M0 y y0) a b =
        descendantOpBlockSum F ρ (M.posteriorCovDiscrepancy M0 y y0) a b ∧
    (opBlock C (M.posteriorCovDiscrepancy M0 y y0) a b = 0 ↔
      ∀ c d, ρ c = a → ρ d = b →
        (F.proj c).comp ((M.posteriorCovDiscrepancy M0 y y0).comp (F.proj d)) = 0) ∧
    ‖opBlock C (M.posteriorCovDiscrepancy M0 y y0) a b‖ ≤ M.covarianceErrorBudget M0 := by
  exact ⟨M.posterior_mean_norm_le_budget M0 y y0,
    M.posterior_covariance_norm_le_budget M0 y y0,
    M.posterior_covariance_refinement M0 C F ρ hRef y y0 a b,
    M.posterior_covariance_block_zero_iff M0 C F ρ hRef y y0 a b,
    M.posterior_covariance_block_norm_le_budget M0 C hC y y0 a b⟩

end Komorebi.FiniteDimensionalGaussianKalman.GaussianModel
