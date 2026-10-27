import AVOC.ApproximateExamples

open Komorebi.AVOC

/-- Deliberately false: opposite Bool point masses do not have zero L1 distance. -/
example : l1RowDistance tightP tightQ = 0 := by
  unfold l1RowDistance
  rw [Fintype.sum_bool]
  norm_num [tightP, tightQ]
