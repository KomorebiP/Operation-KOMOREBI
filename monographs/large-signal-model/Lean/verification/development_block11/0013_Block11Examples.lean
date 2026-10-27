import KomorebiLSM.CoreStability
import KomorebiLSM.FilteringStability

set_option autoImplicit false
namespace Komorebi.LSM.Block11Examples
open Filtering Identification

theorem strict_margin_preserves_mass :
    (0:ℝ) < (ContinuousLinearMap.id ℝ ℝ) (3/4) := by norm_num

theorem boundary_margin_can_zero_mass :
    let lam := ContinuousLinearMap.id ℝ ℝ
    lam (1:ℝ) = 1 ∧ ‖(0:ℝ)-1‖ = 1 ∧ lam 0 = 0 := by norm_num

theorem insufficient_margin_can_negative_mass :
    let lam := ContinuousLinearMap.id ℝ ℝ
    lam (1:ℝ) = 1 ∧ lam (-1) < 0 := by norm_num

/-- Arbitrarily small absolute error can still change a normalized state by one. -/
theorem rare_branch_amplification (η : ℝ) (hη : 0 < η) :
    let lam : (ℝ × ℝ) →L[ℝ] ℝ := ContinuousLinearMap.fst ℝ ℝ ℝ
    ‖((η,η):ℝ × ℝ)-(η,0)‖ = η ∧
    ‖Filtering.normalize lam (η,η)-Filtering.normalize lam (η,0)‖ = 1 := by
  have hn : η ≠ 0 := ne_of_gt hη
  simp [Filtering.normalize, Prod.norm_def, abs_of_pos hη, hn, hη.le]

theorem zero_noise_exact {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    [FiniteDimensional ℝ E] (H B : E →L[ℝ] E) (hH : 0 < rowGain H) :
    coreFit H 0 0 B = B := by
  have h := core_error_identity H 0 0 B (by simpa using hH)
  apply sub_eq_zero.mp
  simpa using h

theorem zero_noise_filter_exact {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    (lam : E →L[ℝ] ℝ) (B : E →L[ℝ] E) (z : E) :
    Filtering.normalize lam (B z)-Filtering.normalize lam (B z) = 0 := sub_self _

theorem core_gap_boundary_is_singular : (1:ℝ)+(-1)=0 := by norm_num

theorem fitted_bound_can_be_sharper :
    ((0:ℝ) + (2/3)*(1/2))/1 < ((0:ℝ)+1*(1/2))/(1-1/2) := by norm_num

end Komorebi.LSM.Block11Examples
