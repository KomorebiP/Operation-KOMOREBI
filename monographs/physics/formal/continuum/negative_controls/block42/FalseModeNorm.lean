import KomorebiPhysics.Relativistic3DFourierL2Generator
open KomorebiPhysics.Relativistic3DFourierL2Generator
example (n : FourierMode) (ψ : HilbertSpinor) :
    ‖modeEmbed n ψ‖ = 2 * ‖ψ‖ := by
  rw [norm_modeEmbed]
