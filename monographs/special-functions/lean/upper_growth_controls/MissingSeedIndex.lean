import CoupledUpperGrowth
open Komorebi.SpecialFunctions.Coupled
open Scales
example : 3 / workedScales.minScale ≤ workedScales.upperRadius 0 := by
  norm_num [minScale, upperRadius, workedScales]
