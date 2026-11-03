import CoupledPositiveReal
open Komorebi.SpecialFunctions.Coupled
open Scales
example (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {R : ℝ} (hR : 0 ≤ R) :
    s.UReal (s.q * (R - 1)) * s.VReal (s.r * (R - 1)) ≤ s.UReal R := by
  exact (s.real_axis_unit_lower hs hstrict hR).1
