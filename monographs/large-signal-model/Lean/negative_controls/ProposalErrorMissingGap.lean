import KomorebiLSM.ProposalError

open Komorebi.LSM.ProposalError

-- The exact reference K=id is injective and its true solution is zero.
-- L=0 has perturbation budget one, but the required positive denominator fails.
example : ‖(1 : ℝ) - 0‖ ≤
    (‖(0 : ℝ →L[ℝ] ℝ) 1 - 0‖ + 1 * ‖(1 : ℝ)‖) /
      (leastSingular (0 : ℝ →L[ℝ] ℝ) - 1) := by
  norm_num [leastSingular, LinearMap.singularValues_zero]
