import KomorebiPhysics.Relativistic3DFourierCompactTime

open KomorebiPhysics.Relativistic3DFourierCompactTime
open KomorebiPhysics.Relativistic3DFourierHilbertStability

example (m h t : ℝ) (a : FourierMode → HilbertSpinor) :
    ‖compactTimePacketResidualL2 m h t ∅ a‖ = 1 := by
  simp [compactTimePacketResidualL2,
    centralHilbertPropagatedPacketL2,
    continuumHilbertPropagatedPacketL2]
