import KomorebiPhysics.Relativistic1DExamples

noncomputable section
open KomorebiPhysics.Dispersion1D
open KomorebiPhysics.Relativistic1DExamples

example : principalFrequency 1 1 (Real.pi / 2) pi_div_two_ne_zero = 3 := by
  rw [principalFrequency_pi_div_two]

end
