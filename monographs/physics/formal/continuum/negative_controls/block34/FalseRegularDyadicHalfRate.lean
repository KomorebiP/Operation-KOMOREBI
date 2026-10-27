import KomorebiPhysics.Relativistic3DRegularConnection

open KomorebiPhysics
open Relativistic3DRegularConnection
open Relativistic3DHilbertScalarDefect

/-- Deliberately false: a quadratic defect falls by `1/4` when the dyadic mesh
is halved, not by `1/2`. -/
example :
    regularDyadicBudget sinusoidalYConnection sinusoidalYBounds 1 1 = (1 : ℝ) / 2 := by
  norm_num [regularDyadicBudget, dyadicMesh, sinusoidalY_regularDerivativeAmplitude]
