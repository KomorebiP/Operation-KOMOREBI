import KomorebiLSM.Block8ApproximationExamples
open Komorebi.LSM.Stability Komorebi.LSM.Reconciliation
open Komorebi.LSM.Block8Examples Komorebi.LSM.Block8ApproximationExamples
example : ‖scaledAtlas.analysis (2:ℝ)‖=‖(2:ℝ)‖ := by
  change ‖(3:ℝ)*2‖=‖(2:ℝ)‖
  norm_num
