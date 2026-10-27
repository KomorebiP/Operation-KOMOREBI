import KomorebiPhysics.CornerExamples

noncomputable section
open KomorebiPhysics KomorebiPhysics.CornerDerivation KomorebiPhysics.CornerCurvature KomorebiPhysics.CornerReconstruction KomorebiPhysics.CornerExamples KomorebiPhysics.PointwiseNoGo
open scoped BigOperators Matrix

example : delta K (delta L Z) - delta L (delta K Z) = - delta (curvature K L) Z := by
  rw [derivation_commutator_on_Z, curvature_action_on_Z_exact]

end
