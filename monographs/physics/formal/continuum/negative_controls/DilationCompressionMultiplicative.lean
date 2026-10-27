import KomorebiPhysics.DilationExamples
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.DilationExamples
-- Deliberately false. Require its own intended diagnostic, not an import failure or timeout.
example : scalarFamily.compressOperator
      (ChannelDilation.coordinate (fun _ : Fin 2 => ℂ) 0 *
       ChannelDilation.coordinate (fun _ : Fin 2 => ℂ) 0) =
    scalarFamily.compressOperator (ChannelDilation.coordinate (fun _ : Fin 2 => ℂ) 0) *
    scalarFamily.compressOperator (ChannelDilation.coordinate (fun _ : Fin 2 => ℂ) 0) := by
  simp only [compression_not_multiplicative]
