import KomorebiLSM.Block7BoundaryExamples
open Komorebi.LSM Komorebi.LSM.BaseNorm Komorebi.LSM.FiniteTV
open Komorebi.LSM.FiniteBayes Komorebi.LSM.FiniteInstruments
open Komorebi.LSM.ObservationTree Komorebi.LSM.Block7Examples Komorebi.LSM.Block7BoundaryExamples
example : distance (observationLaw scalarCone (fixedPolicy 0) echo 1 1)
    (observationLaw scalarCone (fixedPolicy 1) echo 1 1) ≤ 0 := by
  rw [changed_policy_observation_distance]
  norm_num
