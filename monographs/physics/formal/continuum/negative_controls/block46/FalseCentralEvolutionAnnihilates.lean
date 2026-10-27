import KomorebiPhysics.Relativistic3DFullFourierEvolution

open KomorebiPhysics.Relativistic3DFullFourierEvolution

example (m h t : ℝ) (f : CoeffL2) (hf : ‖f‖ = 1) :
    ‖centralCoeffPropagator m h t f‖ = 0 := by
  rw [norm_centralCoeffPropagator, hf]
  norm_num
