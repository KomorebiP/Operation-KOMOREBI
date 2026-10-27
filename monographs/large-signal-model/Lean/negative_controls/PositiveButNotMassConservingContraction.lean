import KomorebiLSM.Block7BoundaryExamples
open Komorebi.LSM Komorebi.LSM.BaseNorm Komorebi.LSM.FiniteTV
open Komorebi.LSM.FiniteBayes Komorebi.LSM.FiniteInstruments
open Komorebi.LSM.ObservationTree Komorebi.LSM.Block7Examples Komorebi.LSM.Block7BoundaryExamples
example : scalarCone.value ((2 : ℝ) • (1 : ℝ)) ≤ scalarCone.value 1 := by
  rw [scalar_value,scalar_value]
  norm_num
