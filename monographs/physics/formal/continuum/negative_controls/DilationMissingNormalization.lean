import KomorebiPhysics.DilationExamples
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.DilationExamples
-- Deliberately false. Require its own intended diagnostic, not an import failure or timeout.
example : (∑ _i : Fin 2, (1:ℂ→L[ℂ]ℂ).adjoint.comp (1:ℂ→L[ℂ]ℂ)) = 1 := by
  simp only [missing_normalization]
