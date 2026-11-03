import CoupledGermInverse
open Komorebi.SpecialFunctions.Coupled.Scales
example : denseOdd (fun n => (n : ℝ)) 3 = (3 : ℂ) := by
  norm_num [denseOdd]
