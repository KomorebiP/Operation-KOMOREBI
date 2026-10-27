import Komorebi.SufficientResolution.GeneralizedDiscrepancyConsistency
import Komorebi.SufficientResolution.TikhonovExamples

/-!
# Exact scalar boundaries for candidate-dependent discrepancy

The good example attains the generalized discrepancy band.  The zero-model example
shows that valid true noise and an operator-error allowance do not, by themselves,
force the candidate-dependent rule to be feasible.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.GeneralizedDiscrepancyExamples

open GeneralizedDiscrepancy GeneralizedDiscrepancySelection
open TikhonovConstruction TikhonovExamples DiscrepancyResidual

 theorem identity_candidate_residual :
    DiscrepancyResidual.residual (scalar 1) 1 (1/4) = (1/5 : ℝ) := by
  have h : (0:ℝ) < 1/4 := by norm_num
  rw [DiscrepancyResidual.residual, recoveryAt_pos (scalar 1) (1/4) h, scalar_regularized, scalar_apply]
  norm_num [Real.norm_eq_abs]

 theorem identity_candidate_source :
    regularized (scalar 1) (1/4) (by norm_num) 1 = (4/5 : ℝ) := by
  rw [scalar_regularized]
  norm_num

 theorem identity_candidate_accepted :
    Accepted (scalar 1) 1 (1/10) 0 2 (4/5 : ℝ) := by
  apply Or.inr
  have hl : (0:ℝ) < 1/4 := by norm_num
  refine ⟨1/4, hl, ?_, ?_, ?_⟩
  · exact identity_candidate_source.symm
  · rw [identity_candidate_residual]
    norm_num [candidateNoise, Real.norm_eq_abs]
  · rw [identity_candidate_residual]
    norm_num [candidateNoise, Real.norm_eq_abs]

 theorem identity_relative_accuracy :
    (0:ℝ)*‖(1:ℝ)‖ < (2-1)*(1/10:ℝ) := by norm_num

 theorem identity_true_noise :
    ‖scalar 1 (1:ℝ)-(1:ℝ)‖ ≤ (1/10:ℝ) := by
  rw [scalar_apply]
  norm_num

 theorem identity_general_existence :
    ∃ x : ℝ, Accepted (scalar 1) 1 (1/10) 0 2 x ∧ ‖x‖ ≤ ‖(1:ℝ)‖ := by
  apply exists_accepted (scalar 1) (scalar 1) (1:ℝ) 1 (1/10) 0 2
  · norm_num
  · norm_num
  · simp
  · exact identity_true_noise
  · exact identity_relative_accuracy

 theorem zero_model_residual (lam : ℝ) (hl : 0 < lam) :
    DiscrepancyResidual.residual (scalar 0) 1 lam = 1 := by
  rw [DiscrepancyResidual.residual, recoveryAt_pos (scalar 0) lam hl, zero_forward_regularized, scalar_apply]
  norm_num

 theorem zero_model_source (lam : ℝ) (hl : 0 < lam) :
    regularized (scalar 0) lam hl 1 = 0 := zero_forward_regularized lam hl 1

 theorem zero_model_not_accepted :
    ∀ x : ℝ, ¬ Accepted (scalar 0) 1 (1/10) 1 2 x := by
  intro x hx
  rcases hx with hs | ⟨lam, hl, hx, _, hhi⟩
  · norm_num at hs
  · have hx0 : x = 0 := by simpa only [zero_forward_regularized] using hx
    subst x
    rw [zero_model_residual lam hl, zero_forward_regularized] at hhi
    norm_num [candidateNoise] at hhi

 theorem zero_model_valid_true_bounds :
    ‖scalar 0-scalar 1‖ ≤ (1:ℝ) ∧
      ‖scalar 1 (1:ℝ)-(1:ℝ)‖ ≤ (1/10:ℝ) := by
  constructor
  · have h : scalar 0-scalar 1 = -(scalar 1) := by
      apply ContinuousLinearMap.ext
      intro y
      simp [scalar_apply]
    rw [h, norm_neg]
    simp [scalar]
  · exact identity_true_noise

 theorem zero_model_relative_accuracy_fails :
    ¬ ((1:ℝ)*‖(1:ℝ)‖ < (2-1)*(1/10:ℝ)) := by norm_num

end Komorebi.SufficientResolution.GeneralizedDiscrepancyExamples
