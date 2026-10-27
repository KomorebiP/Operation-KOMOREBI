import AVOC.ExactRateDistortionExamples

open Komorebi.AVOC

example :
    exactValueCodeNumber twoClusterValue (1 / 2 : ℚ) (by norm_num) = 1 := by
  rw [twoCluster_exact_code_number]
