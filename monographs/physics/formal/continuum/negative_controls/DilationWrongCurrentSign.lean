import KomorebiPhysics.DilationExamples
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.DilationExamples
-- Deliberately false. Require its own intended diagnostic, not an import failure or timeout.
example :
    (ChannelDilation.coordinateAtlas (fun _ : Fin 2 => EuclideanSpace ℂ (Fin 2))).current
      (EffectExamples.softAtlas.sqrtFamily.liftOperator Examples.rotation2)
      (EffectExamples.softAtlas.dilation EffectExamples.softState) 0 1 = 12/25 := by
  rw [soft_dilated_current]
  norm_num
