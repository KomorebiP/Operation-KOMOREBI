import CoupledGermInverse
open Komorebi.SpecialFunctions.Coupled.Scales
example : denseOdd (fun _ => (1 : ℝ)) 3 = (1 / 6 : ℂ) := by
  norm_num [denseOdd]
