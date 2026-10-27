import KomorebiPhysics.Relativistic3DFourierHilbertStability

open KomorebiPhysics.Relativistic3DFourierHilbertStability

example (m h t : ℝ) (n : Mode) (ψ : HilbertSpinor) (hψ : ‖ψ‖ = 1) :
    ‖centralHilbertModePropagator m h n t ψ‖ = 2 := by
  rw [norm_centralHilbertModePropagator, hψ]
  norm_num
