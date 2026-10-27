import KomorebiPhysics.EffectExamples
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : softAtlas.current Examples.rotation2 softState 0 1 = 12/25 := by
  rw [soft_current_nonzero.1]
  norm_num
