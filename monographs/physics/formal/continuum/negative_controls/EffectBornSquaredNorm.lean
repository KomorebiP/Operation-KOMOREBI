import KomorebiPhysics.EffectExamples
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : softAtlas.probability softState 0 = ‖softAtlas.effect 0 softState‖ ^ 2 := by
  rw [soft_probabilities.1, soft_squared_effect_norm]
  norm_num
