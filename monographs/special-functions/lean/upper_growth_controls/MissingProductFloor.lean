import CoupledUpperGrowth
open Komorebi.SpecialFunctions.Coupled.Scales
example : Real.log 1 ≤ Real.log 1 + Real.log 2 + Real.log (1 / 4) + Real.log (1 / 4) := by
  exact log_upper_from_full (f := 1) (R := 1) (u := 1 / 4) (v := 1 / 4)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
