import KomorebiLSM.Block7BoundaryExamples
open Komorebi.LSM Komorebi.LSM.BaseNorm Komorebi.LSM.FiniteTV
open Komorebi.LSM.FiniteBayes Komorebi.LSM.FiniteInstruments
open Komorebi.LSM.ObservationTree Komorebi.LSM.Block7Examples Komorebi.LSM.Block7BoundaryExamples
example : (orthant (Fin 2)).value (![1,-1])=0 := by
  rw [signed_base_norm_two]
  norm_num
