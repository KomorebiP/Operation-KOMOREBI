import KomorebiPhysics.Relativistic3DFourierPropagator

open KomorebiPhysics.Relativistic3DFourierPropagator

/-- Deliberately false: the lattice exponential also equals the identity at time zero. -/
example (m h : ℝ) (n : Mode) : centralModePropagator m h n 0 = 0 := by
  simp
