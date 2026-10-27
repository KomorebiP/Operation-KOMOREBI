import KomorebiPhysics.Relativistic3DFourierCompactTime

open KomorebiPhysics.Relativistic3DFourierCompactTime
open KomorebiPhysics.Relativistic3DFourierHilbertStability

example (m h : ℝ) (n : FourierMode) :
    ‖centralHilbertModePropagator m h n 0 -
      continuumHilbertModePropagator m n 0‖ = 1 := by
  simp [centralHilbertModePropagator, continuumHilbertModePropagator,
    hilbertTimeScaledOperator]
