import KomorebiLSM.Block4Examples

open Komorebi.LSM.FiniteBayes Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block4Examples

example : summaryMass actualDefect = 0 := by
  change actualDefect 0 = 0
  rw [exact_defect_coordinates.1]
  norm_num
