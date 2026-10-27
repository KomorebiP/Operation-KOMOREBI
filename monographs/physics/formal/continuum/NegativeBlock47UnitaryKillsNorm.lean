import KomorebiPhysics.Relativistic3DTorusFourierEvolution
open KomorebiPhysics.Relativistic3DTorusFourierEvolution

example (m t : ℝ) (f : TorusSpinorL2) (hf : ‖f‖ = 1) :
    ‖continuumTorusUnitary m t f‖ = 0 := by
  rw [norm_continuumTorusUnitary, hf]
  norm_num
