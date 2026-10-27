import KomorebiLSM.Block8ApproximationExamples
open Komorebi.LSM.Stability Komorebi.LSM.Reconciliation
open Komorebi.LSM.Block8Examples Komorebi.LSM.Block8ApproximationExamples
example : ‖(0:ℝ)-expandingPrediction 3‖ ≤ 1 := by
  rw [local_error_not_whole_trajectory_error]
  norm_num
