import KomorebiLSM.Block8ApproximationExamples
open Komorebi.LSM.Stability Komorebi.LSM.Reconciliation
open Komorebi.LSM.Block8Examples Komorebi.LSM.Block8ApproximationExamples
example : weightedMean chartWeights (fun _ => (4:ℝ))=0 := by
  rw [unanimous_wrong_fit]
  norm_num
