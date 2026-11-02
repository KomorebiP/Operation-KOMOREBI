import CoupledEntire
open Komorebi.SpecialFunctions.Coupled
open Komorebi.SpecialFunctions.Coupled.Scales

example (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) : deriv s.U 0 = -1 := by
  have h := (s.coupled_entire_equations hs hstrict 0).1
  simpa [U, V, oddSum_zero] using h
