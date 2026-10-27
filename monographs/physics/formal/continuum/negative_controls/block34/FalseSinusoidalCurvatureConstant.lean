import KomorebiPhysics.Relativistic3DRegularConnection

open KomorebiPhysics
open Relativistic3DRegularConnection

/-- Deliberately false: the witness curvature is `cos x`, so its values at
`x=0` and `x=π/2` are different. -/
example :
    curvatureXY sinusoidalYConnection ⟨0, 0, 0⟩ =
      curvatureXY sinusoidalYConnection ⟨Real.pi / 2, 0, 0⟩ := by
  simp
