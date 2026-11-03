import CoupledGrowthTypes
open Komorebi.SpecialFunctions.Coupled.Scales
example : 1 + Real.log 0 / Real.log 2 ≤ Real.log (Real.log 1) / Real.log 2 ∧
    Real.log (Real.log 1) / Real.log 2 ≤ 1 + Real.log 1 / Real.log 2 := by
  exact loglog_ratio_sandwich (f := fun _ => 1) (ρ := 1) (lo := 0) (hi := 1) (R := 2)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num)
