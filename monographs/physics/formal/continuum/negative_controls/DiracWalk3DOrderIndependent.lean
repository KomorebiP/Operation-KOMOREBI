import KomorebiPhysics.Relativistic3DExamples

open KomorebiPhysics.RelativisticClifford3D
open KomorebiPhysics.InvolutionExponential4

example :
    closedFactor alphaX (Real.pi / 2) * closedFactor alphaY (Real.pi / 2) =
      closedFactor alphaY (Real.pi / 2) * closedFactor alphaX (Real.pi / 2) := by
  apply False.elim
