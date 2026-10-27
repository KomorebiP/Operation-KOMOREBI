import CoupledFormal

open Komorebi.SpecialFunctions.Coupled
open Komorebi.SpecialFunctions.Coupled.Scales

example : workedScales.u2 = 1 := by
  norm_num [workedScales, u2, p, k]
