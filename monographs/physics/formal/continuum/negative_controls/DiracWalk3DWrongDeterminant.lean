import KomorebiPhysics.Relativistic3DExamples

open KomorebiPhysics.DiracWalk3D

example : Matrix.det (walk 0 0 0 1 (Real.pi / 2)) = (-1 : ℂ) := by
  apply False.elim
