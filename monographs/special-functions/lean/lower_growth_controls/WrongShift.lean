import CoupledLowerGrowth
open Komorebi.SpecialFunctions.Coupled
open Scales
example : workedScales.maxScale * (11 + workedScales.lowerShift) ≤
    workedScales.maxScale * (11 - 1) - workedScales.lowerShift := by
  norm_num [lowerShift, maxScale, workedScales]
