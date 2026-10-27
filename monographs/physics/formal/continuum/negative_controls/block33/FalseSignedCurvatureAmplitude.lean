import KomorebiPhysics.Relativistic3DAffineConnection

open KomorebiPhysics
open Relativistic3DAffineConnection

/-- Deliberately false: the certified curvature amplitude uses absolute values
and is nonnegative even for a negative magnetic field. -/
example : affineCurvatureAmplitude (uniformBzConnection (-2)) = (-2 : ℝ) := by
  norm_num
