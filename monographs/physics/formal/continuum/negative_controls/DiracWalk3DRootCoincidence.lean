import KomorebiPhysics.Relativistic3DExamples

open KomorebiPhysics.Spectrum3D

example :
    rootMinus 0 0 0 1 (Real.pi / 2) =
      rootPlus 0 0 0 1 (Real.pi / 2) := by
  apply False.elim
