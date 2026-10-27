import AVOC.FiniteCalibration
open Komorebi.AVOC.FiniteCalibration Finset
/-- Must fail: the empirical singleton misses with probability one here. -/
example : (∑ k ∈ range 2,
    if (k : ℚ) = (1/2 : ℚ) then 0 else mass 1 k (1/2)) ≤ 1/10 := by
  rw [empirical_singleton_counterexample]
  norm_num
