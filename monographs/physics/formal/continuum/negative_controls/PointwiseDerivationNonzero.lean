import KomorebiPhysics.CornerExamples

noncomputable section
open KomorebiPhysics KomorebiPhysics.CornerDerivation KomorebiPhysics.CornerCurvature KomorebiPhysics.CornerReconstruction KomorebiPhysics.CornerExamples KomorebiPhysics.PointwiseNoGo
open scoped BigOperators Matrix

example (D : PointAlgebra Idx →ₗ[ℂ] PointAlgebra Idx) (hD : IsDerivation D) : D ≠ 0 := by
  rw [two_point_no_go D hD]

end
