import AVOC.ObservationCensoring

open Komorebi.AVOC.ObservationCensoring

/-- Must fail: losing every rejection turns a fair source into certain success
among retained reports, so the original parameter is not preserved. -/
example : conditionalSuccess (1 / 2) 1 0 (by norm_num) (by norm_num)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) = (1 / 2 : ℚ) := by
  rw [outcome_dependent_censoring_counterexample]
  norm_num
