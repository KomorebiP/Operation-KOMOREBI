import KomorebiPhysics.Relativistic3DFullFourierEvolution

open KomorebiPhysics.Relativistic3DFullFourierEvolution

example (m t : ℝ) (f : CoeffL2) (hf : ‖f‖ = 1) :
    ‖continuumCoeffPropagator m t f‖ = 2 := by
  rw [norm_continuumCoeffPropagator, hf]
  norm_num
