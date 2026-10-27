import KomorebiLSM.Block8ApproximationExamples
open Komorebi.LSM.Stability Komorebi.LSM.Reconciliation
open Komorebi.LSM.Block8Examples Komorebi.LSM.Block8ApproximationExamples
example : weightedMean chartWeights chartFits=3 := by
  rw [chart_mean]
  norm_num
