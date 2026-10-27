import Komorebi.FDPosteriorMeanBounds

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman.GaussianModel
open MeasureTheory Komorebi.BayesianPosteriorPerturb
variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]

/-- The actual posterior mean discrepancy retains its exact three-source identity. -/
theorem posterior_mean_exact (M M0 : GaussianModel ι κ) (y y0 : EuclideanSpace ℝ κ) :
    (∫ x, x ∂M.posteriorLaw y) - (∫ x, x ∂M0.posteriorLaw y0) =
      (M.mean - M0.mean) +
      (M.gainOp - M0.gainOp) (y - M.observationOp M.mean) +
      M0.gainOp ((y-y0) - (M.observationOp - M0.observationOp) M.mean -
        M0.observationOp (M.mean - M0.mean)) := by
  rw [posterior_expectation, posterior_expectation]
  exact kalmanPosteriorMean_sub_exact M.gainOp M0.gainOp
    M.observationOp M0.observationOp M.mean M0.mean y y0

/-- Six exact residual terms for actual posterior covariance operators. -/
theorem posterior_covariance_six_term (M M0 : GaussianModel ι κ)
    (y y0 : EuclideanSpace ℝ κ) :
    let A := kalmanClosedLoop M.gainOp M.observationOp
    let A0 := kalmanClosedLoop M0.gainOp M0.observationOp
    M.posteriorCovDiscrepancy M0 y y0 =
      (A-A0).comp (M.priorOp.comp A.adjoint) +
      A0.comp ((M.priorOp-M0.priorOp).comp A.adjoint) +
      A0.comp (M0.priorOp.comp (A.adjoint-A0.adjoint)) +
      (M.gainOp-M0.gainOp).comp (M.noiseOp.comp M.gainOp.adjoint) +
      M0.gainOp.comp ((M.noiseOp-M0.noiseOp).comp M.gainOp.adjoint) +
      M0.gainOp.comp (M0.noiseOp.comp (M.gainOp.adjoint-M0.gainOp.adjoint)) := by
  dsimp only
  rw [posteriorCovDiscrepancy_eq_operator]
  exact josephPosteriorCov_sub_exact M.gainOp M0.gainOp
    M.observationOp M0.observationOp M.priorOp M0.priorOp M.noiseOp M0.noiseOp

end Komorebi.FiniteDimensionalGaussianKalman.GaussianModel
