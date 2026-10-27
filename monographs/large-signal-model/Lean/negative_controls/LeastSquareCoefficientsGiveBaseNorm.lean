import KomorebiLSM.Block7BoundaryExamples
open Komorebi.LSM Komorebi.LSM.BaseNorm Komorebi.LSM.FiniteTV
open Komorebi.LSM.FiniteBayes Komorebi.LSM.FiniteInstruments
open Komorebi.LSM.ObservationTree Komorebi.LSM.Block7Examples Komorebi.LSM.Block7BoundaryExamples
example : redundantCone.value (redundantSynthesis leastSquareCoefficients)=l1 leastSquareCoefficients := by
  rw [redundant_same_state,redundant_base_norm_one,redundant_coefficients_l1]
  norm_num
