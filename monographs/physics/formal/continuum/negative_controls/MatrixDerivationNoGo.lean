import KomorebiPhysics.CornerExamples

noncomputable section
open KomorebiPhysics KomorebiPhysics.CornerDerivation KomorebiPhysics.CornerCurvature KomorebiPhysics.CornerReconstruction KomorebiPhysics.CornerExamples KomorebiPhysics.PointwiseNoGo
open scoped BigOperators Matrix

example : delta K L = 0 := by
  rw [delta_K_L_exact]

end
