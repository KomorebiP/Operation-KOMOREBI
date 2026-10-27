import KomorebiLSM.Block7BoundaryExamples
open Komorebi.LSM Komorebi.LSM.BaseNorm Komorebi.LSM.FiniteTV
open Komorebi.LSM.FiniteBayes Komorebi.LSM.FiniteInstruments
open Komorebi.LSM.ObservationTree Komorebi.LSM.Block7Examples Komorebi.LSM.Block7BoundaryExamples
example : distance (conditional (sharpP (1/100)) sharpEvent)
    (conditional (sharpQ (1/100) (1/200)) sharpEvent) ≤ 1/200 := by
  rw [rare_event_conditional_distance]
  norm_num
