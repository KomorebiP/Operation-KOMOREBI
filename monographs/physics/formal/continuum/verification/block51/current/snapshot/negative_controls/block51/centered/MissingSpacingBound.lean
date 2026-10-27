import KomorebiPhysics.Relativistic3DCenteredConvergence
open KomorebiPhysics Relativistic3DCenteredConvergence

-- Deliberately invalid interface use: the supplied bound theorem requires h ≠ 0.
example (m h : ℝ) : ‖centeredCoeffOperator m h‖ ≤ Real.sqrt (m^2+3*h⁻¹^2) := by
  exact centeredCoeffOperator_norm_le m h
