import KomorebiLSM.Block8ApproximationExamples
open Komorebi.LSM.Stability Komorebi.LSM.Reconciliation
open Komorebi.LSM.Block8Examples Komorebi.LSM.Block8ApproximationExamples
example : ‖((scale (rate 1))^2) (1:ℝ)-1‖ ≤ 1/2 := by
  rw [refinement_horizon_cannot_be_exchanged.2]
  norm_num
