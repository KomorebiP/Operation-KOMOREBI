import KomorebiPhysics.Relativistic3DExamples

open KomorebiPhysics.Dispersion3D

example : phase 0 0 0 1 (Real.pi / 2) = -(Real.pi / 2) := by
  apply False.elim
