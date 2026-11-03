import CoupledCharacteristic
open Komorebi.SpecialFunctions.Coupled
open Scales
example (s : Scales) : (1 - s.q ^ (0 : ℝ)) * (1 - s.b ^ (0 : ℝ)) =
    (s.a * s.r) ^ (0 : ℝ) := by
  norm_num
