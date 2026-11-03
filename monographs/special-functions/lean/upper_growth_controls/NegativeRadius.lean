import CoupledUpperGrowth
open Komorebi.SpecialFunctions.Coupled
open Scales
example : workedScales.UReal (-1) ≤ (-1) *
    (1 + workedScales.UReal (workedScales.q * (-1)) * workedScales.VReal (workedScales.r * (-1))) := by
  exact (workedScales.real_axis_full_upper workedScales_positive
    (by norm_num [workedScales]) (R := -1) (by norm_num)).1
