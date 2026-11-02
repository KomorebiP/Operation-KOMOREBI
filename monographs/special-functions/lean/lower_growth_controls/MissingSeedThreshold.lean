import CoupledLowerGrowth
open Komorebi.SpecialFunctions.Coupled
open Scales
example : workedScales.LowerPowerAt 1 ![1, 1] 0 := by
  exact workedScales.lower_power_seed workedScales_positive (by norm_num [workedScales])
    (ρ := 1) (by norm_num) (w := ![1, 1]) (by intro i; fin_cases i <;> norm_num)
    (R := 0) (by norm_num) (by norm_num [lowerThreshold, minScale, workedScales])
