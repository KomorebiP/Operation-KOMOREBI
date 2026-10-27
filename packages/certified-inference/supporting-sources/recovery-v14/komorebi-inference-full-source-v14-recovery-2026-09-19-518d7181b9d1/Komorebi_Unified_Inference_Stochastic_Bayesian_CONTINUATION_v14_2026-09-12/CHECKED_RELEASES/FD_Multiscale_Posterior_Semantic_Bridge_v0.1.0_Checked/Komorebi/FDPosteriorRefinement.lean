import Komorebi.FDPosteriorMeanBounds

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman.GaussianModel
open Komorebi.AbstractProjectorRefinement Komorebi.BayesianPosteriorPerturb

variable {ι κ : Type*} [Fintype ι] [Fintype κ] [DecidableEq ι] [DecidableEq κ]
variable {cLane fLane : Type*} [Fintype cLane] [Fintype fLane] [DecidableEq cLane]

/-- The actual posterior covariance discrepancy has the exact inherited refinement. -/
theorem posterior_covariance_refinement (M M0 : GaussianModel ι κ)
    (C : ProjectorFamily (EuclideanSpace ℝ ι) cLane)
    (F : ProjectorFamily (EuclideanSpace ℝ ι) fLane)
    (ρ : fLane → cLane) (hRef : Refines C F ρ)
    (y y0 : EuclideanSpace ℝ κ) (a b : cLane) :
    opBlock C (M.posteriorCovDiscrepancy M0 y y0) a b =
      descendantOpBlockSum F ρ (M.posteriorCovDiscrepancy M0 y y0) a b := by
  simpa only [posteriorCovDiscrepancy_eq_operator] using
    posteriorCovError_opBlock_refinement C F ρ hRef M.gainOp M0.gainOp
      M.observationOp M0.observationOp M.priorOp M0.priorOp M.noiseOp M0.noiseOp a b

/-- No cancellation among resolved corners of the actual posterior covariance error.
This is not an identifiability theorem for the primitive model parameters. -/
theorem posterior_covariance_block_zero_iff (M M0 : GaussianModel ι κ)
    (C : ProjectorFamily (EuclideanSpace ℝ ι) cLane)
    (F : ProjectorFamily (EuclideanSpace ℝ ι) fLane)
    (ρ : fLane → cLane) (hRef : Refines C F ρ)
    (y y0 : EuclideanSpace ℝ κ) (a b : cLane) :
    opBlock C (M.posteriorCovDiscrepancy M0 y y0) a b = 0 ↔
      ∀ c d, ρ c = a → ρ d = b →
        (F.proj c).comp ((M.posteriorCovDiscrepancy M0 y y0).comp (F.proj d)) = 0 := by
  simpa only [posteriorCovDiscrepancy_eq_operator] using
    posteriorCovError_opBlock_zero_iff_descendants_zero C F ρ hRef M.gainOp M0.gainOp
      M.observationOp M0.observationOp M.priorOp M0.priorOp M.noiseOp M0.noiseOp a b

/-- A nonzero actual coarse posterior error has a nonzero resolved descendant. -/
theorem posterior_covariance_block_nonzero_iff (M M0 : GaussianModel ι κ)
    (C : ProjectorFamily (EuclideanSpace ℝ ι) cLane)
    (F : ProjectorFamily (EuclideanSpace ℝ ι) fLane)
    (ρ : fLane → cLane) (hRef : Refines C F ρ)
    (y y0 : EuclideanSpace ℝ κ) (a b : cLane) :
    opBlock C (M.posteriorCovDiscrepancy M0 y y0) a b ≠ 0 ↔
      ∃ c d, ρ c = a ∧ ρ d = b ∧
        (F.proj c).comp ((M.posteriorCovDiscrepancy M0 y y0).comp (F.proj d)) ≠ 0 := by
  simpa only [posteriorCovDiscrepancy_eq_operator] using
    posteriorCovError_opBlock_ne_zero_iff_exists_descendant C F ρ hRef M.gainOp M0.gainOp
      M.observationOp M0.observationOp M.priorOp M0.priorOp M.noiseOp M0.noiseOp a b

/-- Operator norm is controlled by a sum of descendant norms, not by an asserted square sum. -/
theorem posterior_covariance_block_norm_le_descendants (M M0 : GaussianModel ι κ)
    (C : ProjectorFamily (EuclideanSpace ℝ ι) cLane)
    (F : ProjectorFamily (EuclideanSpace ℝ ι) fLane)
    (ρ : fLane → cLane) (hRef : Refines C F ρ)
    (y y0 : EuclideanSpace ℝ κ) (a b : cLane) :
    ‖opBlock C (M.posteriorCovDiscrepancy M0 y y0) a b‖ ≤
      descendantNormBudget F ρ (M.posteriorCovDiscrepancy M0 y y0) a b := by
  simpa only [posteriorCovDiscrepancy_eq_operator] using
    posteriorCovError_opBlock_norm_le_descendantBudget C F ρ hRef M.gainOp M0.gainOp
      M.observationOp M0.observationOp M.priorOp M0.priorOp M.noiseOp M0.noiseOp a b

omit [DecidableEq cLane] in
/-- Each contractive coarse corner of the actual posterior error satisfies the residual budget. -/
theorem posterior_covariance_block_norm_le_budget (M M0 : GaussianModel ι κ)
    (C : ProjectorFamily (EuclideanSpace ℝ ι) cLane) (hC : ∀ a, ‖C.proj a‖ ≤ 1)
    (y y0 : EuclideanSpace ℝ κ) (a b : cLane) :
    ‖opBlock C (M.posteriorCovDiscrepancy M0 y y0) a b‖ ≤ M.covarianceErrorBudget M0 := by
  exact (opBlock_norm_le_global_of_contractive C hC _ a b).trans
    (M.posterior_covariance_norm_le_budget M0 y y0)

end Komorebi.FiniteDimensionalGaussianKalman.GaussianModel
