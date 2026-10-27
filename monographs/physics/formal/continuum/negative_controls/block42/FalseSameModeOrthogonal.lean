import KomorebiPhysics.Relativistic3DFourierL2Generator
open KomorebiPhysics.Relativistic3DFourierL2Generator
example (n : FourierMode) (ψ : HilbertSpinor) :
    inner ℂ (modeEmbed n ψ) (modeEmbed n ψ) = 0 := by
  rw [inner_modeEmbed]
  simp
