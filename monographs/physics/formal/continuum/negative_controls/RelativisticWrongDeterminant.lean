import KomorebiPhysics.Relativistic1DExamples

noncomputable section
open KomorebiPhysics.DiracWalk1D

example : Matrix.det (update 1 1 (Real.pi / 2)) = -1 := by
  rw [det_update]

end
