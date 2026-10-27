import KomorebiPhysics.Relativistic3DFourierL2Generator
open KomorebiPhysics.Relativistic3DFourierL2Generator
example (S : Finset FourierMode) (a : FourierMode → HilbertSpinor) :
    ‖fourierPacketL2 S a‖ ^ 2 = 0 := by
  rw [fourierPacketL2_norm_sq]
  simp
