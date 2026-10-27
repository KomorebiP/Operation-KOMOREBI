import KomorebiPhysics.Relativistic3DFourierCompactTime

open KomorebiPhysics.Relativistic3DFourierCompactTime

example : ‖-(Complex.I * ((1 : ℝ) : ℂ))‖ = 0 := by
  rw [norm_schrodingerCoefficient]
  norm_num
