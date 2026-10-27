import KomorebiLSM.Block5Examples

open Komorebi.LSM.Behavior Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block5Examples

example : tableState process selected [] 1 = 1 := by
  rw [learned_initial]
  norm_num
