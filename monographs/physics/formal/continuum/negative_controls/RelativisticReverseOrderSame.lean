import KomorebiPhysics.Relativistic1DExamples

noncomputable section
open KomorebiPhysics.DiracWalk1D
open KomorebiPhysics.Relativistic1DExamples

example : massStep 1 (Real.pi / 2) * shiftStep 1 (Real.pi / 2) =
    shiftStep 1 (Real.pi / 2) * massStep 1 (Real.pi / 2) := by
  apply False.elim

end
