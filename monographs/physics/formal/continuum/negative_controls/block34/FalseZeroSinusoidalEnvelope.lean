import KomorebiPhysics.Relativistic3DRegularConnection

open KomorebiPhysics
open Relativistic3DRegularConnection

/-- Deliberately false: `A_y(x)=sin x` has a nonzero certified derivative
envelope. -/
example :
    regularDerivativeAmplitude sinusoidalYConnection sinusoidalYBounds = 0 := by
  norm_num
