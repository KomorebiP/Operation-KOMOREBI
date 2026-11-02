import CoupledPositiveReal
open Komorebi.SpecialFunctions.Coupled
open Scales
example (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    ‖s.U ((-1 : ℝ) : ℂ)‖ = s.UReal (-1) := by
  exact (s.real_axis_norm hs hstrict (R := -1) (by norm_num)).1
