import KomorebiPhysics.DilationExamples
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.DilationExamples
-- Deliberately false. Require its own intended diagnostic, not an import failure or timeout.
example : CycleGauge.triangle = 0 := by
  simp only [CycleGauge.triangle_nonzero]
