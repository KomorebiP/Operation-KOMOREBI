import KomorebiLSM.Block5Examples

open Komorebi.LSM.Behavior Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block5Examples

example : haarDetail.mulVec ![(3/4 : ℝ),1/4] = 0 := by
  rw [haar_detail_signed]
  ext i
  fin_cases i <;> norm_num
