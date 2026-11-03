import CoupledEntire
open Komorebi.SpecialFunctions.Coupled.Scales

-- The first recurrence denominator is three, not two.
example : nextCoefficient (1 / 2) (1 / 2) (fun _ => (1, 1)) 0 = (1 / 8 : ℝ) := by
  norm_num [nextCoefficient]
