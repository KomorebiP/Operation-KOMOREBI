import KomorebiLSM.Block4Examples

open Komorebi.LSM.FiniteBayes Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block4Examples

example : coinOne.branch ((),true) = coinTwo.branch ((),true) := by
  simp only [coins_branches_distinct]
