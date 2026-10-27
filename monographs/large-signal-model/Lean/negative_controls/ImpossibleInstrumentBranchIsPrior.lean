import KomorebiLSM.Block4Examples

open Komorebi.LSM.FiniteBayes Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block4Examples

example : IsPrior
    (normalize mass ((coinInstrument 0 le_rfl (by norm_num)).branch ((),true) (pointMass 0))) := by
  simp only [impossible_branch_not_prior]
