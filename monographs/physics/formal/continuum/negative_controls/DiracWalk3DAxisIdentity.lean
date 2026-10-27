import KomorebiPhysics.Relativistic3DExamples

open KomorebiPhysics.RelativisticClifford3D
open KomorebiPhysics.DiracWalk3D

example : walk 0 0 0 1 (Real.pi / 2) = (1 : Mat4) := by
  apply False.elim
