import CoupledFormal

open Komorebi.SpecialFunctions.Coupled
open Komorebi.SpecialFunctions.Coupled.Scales

example : (0 : ℝ) < (Scales.mk (-1) 1 1 1).u1 := by
  norm_num [u1, p]
