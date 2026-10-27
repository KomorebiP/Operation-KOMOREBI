import Komorebi.GeneratedRoundedScalar

set_option autoImplicit false
set_option maxRecDepth 16384
set_option maxHeartbeats 4000000
namespace Komorebi.RoundedPosterior.RoundedBoundaryChecks
open Komorebi.ExactPosterior
open GeneratedRoundedScalar

/-- The rounded residual center alone can be zero even though the exact residual is nonzero. -/
theorem rounded_center_is_zero : (residualBall 4 model gain 0 0).center = 0 := by decide +kernel

theorem exact_residual_is_nonzero : model.residual gain 0 0 = -(1/1024 : ℚ) := by decide +kernel

theorem propagated_radius_is_nonzero : (residualBall 4 model gain 0 0).radius = (1/8 : ℚ) := by decide +kernel

theorem dropping_radius_is_invalid : ¬ Encloses ⟨0,0⟩ (model.residual gain 0 0) := by
  unfold Encloses
  decide +kernel

/-- The universal enclosure theorem covers that cancellation example. -/
theorem cancellation_is_enclosed : Encloses (residualBall 4 model gain 0 0) (model.residual gain 0 0) :=
  residualBall_encloses 4 model gain 0 0

theorem tight_tolerance_rejected : checkTolerance model candidate0 (1/10000) = false := by decide +kernel

theorem coarse_return_rejected : certifyRounded 4 model outputs inputs gain (1/500) = none := by
  rw [certifyRounded, ite_eq_left setup_valid]
  change (if checkTolerance model candidate0 (1/500) then some candidate0 else none) = none
  rw [tolerance0_computed]
  rfl

/-- The actual precision schedule skips the rejected coarse calculation. -/
theorem actual_precision_search_return :
    certifyPrecisions [4,12] model outputs inputs gain (1/500) = some candidate1 := by
  simp only [certifyPrecisions, coarse_return_rejected, successful_return]

end Komorebi.RoundedPosterior.RoundedBoundaryChecks
