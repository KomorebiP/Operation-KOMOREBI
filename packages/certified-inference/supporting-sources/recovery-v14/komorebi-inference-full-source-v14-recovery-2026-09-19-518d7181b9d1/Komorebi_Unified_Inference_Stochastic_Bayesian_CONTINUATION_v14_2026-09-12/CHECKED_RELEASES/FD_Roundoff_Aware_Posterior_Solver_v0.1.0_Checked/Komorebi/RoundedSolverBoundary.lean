import Komorebi.GeneratedRoundedGainScalar
import Komorebi.RoundedSolverOrigin

set_option autoImplicit false
namespace Komorebi.RoundoffSolver.Boundary
open Matrix Komorebi.ExactPosterior Komorebi.RoundedPosterior
open GeneratedRoundedGainScalar

/-- A fixed coarse arithmetic graph is not the adaptive-precision solver. -/
def coarseStep (B : Matrix (Fin 1) (Fin 1) ℚ) : Matrix (Fin 1) (Fin 1) ℚ :=
  fun i j => (updateBall 0 model B i j).center

theorem coarse_zero_fixed : coarseStep 0 = 0 := by decide +kernel

/-- Repeating the coarse computation can stagnate forever away from the exact gain. -/
theorem coarse_stagnates (n : ℕ) : iterate coarseStep 0 n = 0 := by
  induction n with
  | zero => rfl
  | succ n ih => rw [iterate_succ,ih,coarse_zero_fixed]

theorem stagnated_residual_nonzero (n : ℕ) :
    rationalEnergy (model.residual (iterate coarseStep 0 n)) = 1 := by
  rw [coarse_stagnates]
  decide +kernel

theorem actual_gain_is_not_exact_iterate : finalGain ≠ model.solverGain initial 4 := by
  decide +kernel

theorem first_update_precision : updatePrecision model 20 initial = 36 := by decide +kernel

theorem large_gain_needs_more_bits : updatePrecision model 20 (!![1000000]) >
    updatePrecision model 20 initial := by decide +kernel

theorem zero_tolerance_rejected : solveRounded model outputs inputs 0 [] initial = none := by
  decide +kernel

def invalidModel := { model with noiseFloor := 0 }

theorem invalid_floor_rejected : solveRounded invalidModel outputs inputs (1/20) [] initial = none := by
  decide +kernel

end Komorebi.RoundoffSolver.Boundary
