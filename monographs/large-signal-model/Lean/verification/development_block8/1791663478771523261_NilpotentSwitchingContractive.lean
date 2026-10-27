import KomorebiLSM.Block8ApproximationExamples
open Komorebi.LSM.Stability Komorebi.LSM.Reconciliation
open Komorebi.LSM.Block8Examples Komorebi.LSM.Block8ApproximationExamples
example : ‖((switchB.comp switchA)^3) (0,1)‖ ≤ 1 := by
  rw [alternating_three_pairs]
  norm_num
