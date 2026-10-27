import KomorebiPhysics.Relativistic3DFourierHilbertStability

open KomorebiPhysics.Relativistic3DFourierHilbertStability

example (m t : ℝ) (S : Finset Mode) (a : Mode → HilbertSpinor)
    (henergy : (∑ n ∈ S, ‖a n‖ ^ 2) = 1) :
    ‖continuumHilbertPropagatedPacketL2 m t S a‖ ^ 2 = 0 := by
  rw [continuumHilbertPropagatedPacketL2_norm_sq, henergy]
  norm_num
