import KomorebiPhysics.Relativistic3DFourierPropagator

open KomorebiPhysics.Relativistic3DFourierPropagator

/-- Deliberately false: exponential evolution at time zero is the identity, not zero. -/
example (m : ℝ) (n : Mode) : continuumModePropagator m n 0 = 0 := by
  simp
