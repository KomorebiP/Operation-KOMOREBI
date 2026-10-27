import KomorebiLSM.Block4Examples

open Komorebi.LSM.FiniteBayes Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block4Examples

example : invisibleDirection = 0 := by
  simp only [invisible_is_not_zero]
