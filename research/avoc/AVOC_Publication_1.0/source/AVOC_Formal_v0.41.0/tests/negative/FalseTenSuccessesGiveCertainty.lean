import AVOC.FiniteCalibration
open Komorebi.AVOC.FiniteCalibration
/-- Must fail: all observed successes do not collapse the probability band. -/
example : lower 10 10 10 (1/10) = 1 := by
  rw [ten_successes_lower]
  norm_num
