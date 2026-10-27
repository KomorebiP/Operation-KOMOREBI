import KomorebiPhysics.Relativistic3DExamples

open KomorebiPhysics.RelativisticClifford3D
open KomorebiPhysics.DiracWalk3D

example (z : ℂ) :
    Matrix.det (z • (1 : Mat4) - walk 0 0 0 1 (Real.pi / 2)) = z ^ 2 + 1 := by
  apply False.elim
