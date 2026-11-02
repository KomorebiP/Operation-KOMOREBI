import CoupledAnalytic
open Komorebi.SpecialFunctions.Coupled
open Komorebi.SpecialFunctions.Coupled.Scales

example (s : Scales) (hs : s.positive)
    (hsmall : s.q ≤ 1 ∧ s.r ≤ 1 ∧ s.a ≤ 1 ∧ s.b ≤ 1) : deriv s.U 0 = 0 := by
  have h := (s.coupled_initial_derivatives hs hsmall).1
  simpa using h
