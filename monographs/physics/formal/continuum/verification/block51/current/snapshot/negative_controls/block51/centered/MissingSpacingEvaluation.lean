import KomorebiPhysics.Relativistic3DCenteredConvergence
open KomorebiPhysics Relativistic3DCenteredConvergence Relativistic3DFourierHilbertStability

-- Deliberately invalid: the evaluation theorem requires h ≠ 0.
example (m h : ℝ) (f : Relativistic3DCenteredConvergence.CoeffL2)
    (n : Relativistic3DCenteredConvergence.Mode) :
    centeredCoeffOperator m h f n = centralHilbertModeOperator m h n (f n) := by
  exact centeredCoeffOperator_apply m h
