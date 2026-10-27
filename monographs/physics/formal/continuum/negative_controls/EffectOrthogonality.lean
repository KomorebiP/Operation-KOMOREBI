import KomorebiPhysics.EffectExamples
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : softAtlas.effect 0 * softAtlas.effect 1 = 0 := by
  simp only [soft_not_orthogonal]
