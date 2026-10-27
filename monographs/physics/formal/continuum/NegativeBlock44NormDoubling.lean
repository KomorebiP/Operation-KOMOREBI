import KomorebiPhysics.Relativistic3DFourierHilbertStability

open KomorebiPhysics.Relativistic3DFourierHilbertStability

example (m t : ℝ) (n : Mode) (ψ : HilbertSpinor) (hψ : ‖ψ‖ = 1) :
    ‖continuumHilbertModePropagator m n t ψ‖ = 2 := by
  rw [norm_continuumHilbertModePropagator, hψ]
  norm_num
