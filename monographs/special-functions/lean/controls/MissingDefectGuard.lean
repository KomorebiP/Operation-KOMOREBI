import CoupledFormal

open Komorebi.SpecialFunctions.Coupled
open Komorebi.SpecialFunctions.Coupled.Scales

example : boundaryLeft.q = boundaryRight.q := by
  norm_num [boundaryLeft, boundaryRight]
