import KomorebiPhysics.CornerExamples

noncomputable section
open KomorebiPhysics KomorebiPhysics.CornerDerivation KomorebiPhysics.CornerCurvature KomorebiPhysics.CornerReconstruction KomorebiPhysics.CornerExamples KomorebiPhysics.PointwiseNoGo
open scoped BigOperators Matrix

example : Matrix.trace (delta K L * delta K L) = Matrix.trace (L * delta K (delta K L)) := by
  rw [exact_trace_ibp_nonzero_left, exact_trace_ibp_nonzero_right]

end
