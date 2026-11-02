import CoupledPositiveReal
open Komorebi.SpecialFunctions.Coupled
open Scales
example : 2 ≤ workedScales.q * (1 - 1) := by
  exact (workedScales.lower_child_radii workedScales_positive (R := 1)
    (by norm_num [lowerThreshold, minScale, workedScales])).1
