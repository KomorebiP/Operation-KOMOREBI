import CoupledFormal

open Komorebi.SpecialFunctions.Coupled
open Komorebi.SpecialFunctions.Coupled.Scales

example : workedScales.defect = 189 / 3125000 := by
  norm_num [workedScales, defect, u2, v2, p, k]
