import KomorebiPhysics.Relativistic3DAffineConnection

open KomorebiPhysics
open Relativistic3DAffineConnection
open Relativistic3DHilbertScalarDefect

/-- Deliberately false: a quadratic defect on a halved mesh drops by `1/4`,
not by `1/2`. -/
example : affineDyadicBudget (uniformBzConnection 1) 1 1 = (1 : ℝ) / 2 := by
  norm_num [affineDyadicBudget, dyadicMesh, affineCurvatureAmplitude,
    uniformBzConnection, curvatureXY, curvatureXZ, curvatureYZ]
