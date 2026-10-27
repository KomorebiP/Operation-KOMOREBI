import KomorebiLSM.Block7BoundaryExamples
open Komorebi.LSM Komorebi.LSM.BaseNorm Komorebi.LSM.FiniteTV
open Komorebi.LSM.FiniteBayes Komorebi.LSM.FiniteInstruments
open Komorebi.LSM.ObservationTree Komorebi.LSM.Block7Examples Komorebi.LSM.Block7BoundaryExamples
example : distance (recordLaw scalarCone (fun _ => bernoulli 0) 1 [] 1)
    (recordLaw scalarCone (fun _ => bernoulli (1/2)) 1 [] 1) ≤ 1/4 := by
  rw [bernoulli_zero_half_one_step]
  norm_num
