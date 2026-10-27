import KomorebiPhysics.Relativistic3DTorusFourierEvolution
open KomorebiPhysics.Relativistic3DTorusFourierEvolution

example (f : TorusSpinorL2) (hf : ‖f‖ = 1) :
    ‖torusFourierEquiv f‖ = 2 := by
  rw [torusFourierEquiv.norm_map, hf]
  norm_num
