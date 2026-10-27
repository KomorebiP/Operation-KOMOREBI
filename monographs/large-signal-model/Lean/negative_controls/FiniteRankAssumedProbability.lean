import KomorebiLSM.Block5Examples

open Komorebi.LSM.Behavior Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block5Examples

example : 0 ≤ signedProcess [()] := by
  rw [finite_rank_is_not_probability]
  norm_num
