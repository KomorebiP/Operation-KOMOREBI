import KomorebiPhysics.EffectExamples
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : (∑ _i : Fin 2, (1 : ℂ →L[ℂ] ℂ)) = 1 := by
  simp only [duplicated_identity_not_complete]
