import KomorebiPhysics.Relativistic1DExamples

noncomputable section
open KomorebiPhysics.DiracWalk1D
open KomorebiPhysics.Dispersion1D

example : Matrix.trace (update 0 0 1) = 4 := by
  rw [trace_eq_two_shell]
  norm_num [shell]

end
