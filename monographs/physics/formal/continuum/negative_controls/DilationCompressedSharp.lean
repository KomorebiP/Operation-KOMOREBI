import KomorebiPhysics.DilationExamples
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.DilationExamples
-- Deliberately false. Require its own intended diagnostic, not an import failure or timeout.
example : scalarFamily.effectAtlas.effect 0 * scalarFamily.effectAtlas.effect 0 = scalarFamily.effectAtlas.effect 0 := by
  simp only [compressed_effect_not_idempotent]
