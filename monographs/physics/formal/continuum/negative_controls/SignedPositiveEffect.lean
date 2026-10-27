import KomorebiPhysics.EffectExamples
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : 0 ≤ effectExpectation ((-1 : ℂ) • (1 : ℂ →L[ℂ] ℂ)) 1 := by
  rw [signed_effect_negative]
  norm_num
