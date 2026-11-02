import CoupledUniqueness
open Komorebi.SpecialFunctions.Coupled
open Komorebi.SpecialFunctions.Coupled.Scales

-- Index zero is the coefficient of z and equals one in both components.
example (s : Scales) : s.coefficients 0 = (0, 0) := by
  rw [coefficients_zero]
  norm_num
