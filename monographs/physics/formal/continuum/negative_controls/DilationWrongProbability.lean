import KomorebiPhysics.DilationExamples
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.DilationExamples
-- Deliberately false. Require its own intended diagnostic, not an import failure or timeout.
example : scalarFamily.effectAtlas.probability 1 0 = 3/5 := by
  rw [scalar_probabilities.1]
  norm_num
