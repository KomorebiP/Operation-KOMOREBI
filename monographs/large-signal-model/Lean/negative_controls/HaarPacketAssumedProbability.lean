import KomorebiLSM.Block5Examples

open Komorebi.LSM.Behavior Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block5Examples

example : 0 ≤ haarDetail.mulVec ![(3/4 : ℝ),1/4] 1 := by
  rw [haar_detail_signed]
  norm_num
