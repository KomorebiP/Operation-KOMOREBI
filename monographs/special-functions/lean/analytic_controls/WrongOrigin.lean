import CoupledAnalytic
open Komorebi.SpecialFunctions.Coupled
open Komorebi.SpecialFunctions.Coupled.Scales

example (s : Scales) : s.U 0 = 1 := by
  simp [U, oddSum_zero]
