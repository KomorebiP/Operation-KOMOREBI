import KomorebiPhysics.Relativistic3DTorusFourierEvolution
open KomorebiPhysics.Relativistic3DTorusFourierEvolution
open KomorebiPhysics.Relativistic3DFourierL2Generator

example (n : Mode)
    (ψ : KomorebiPhysics.Relativistic3DTorusFourierEvolution.HilbertSpinor)
    (hψ : ‖ψ‖ = 1) :
    ‖torusFourierEquiv (modeEmbedIsometry n ψ)‖ = 0 := by
  rw [torusFourierEquiv.norm_map, (modeEmbedIsometry n).norm_map, hψ]
  norm_num
