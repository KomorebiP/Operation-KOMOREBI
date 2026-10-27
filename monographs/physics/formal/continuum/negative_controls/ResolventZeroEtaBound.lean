import KomorebiPhysics.ResolventExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.ResolventDomain
open KomorebiPhysics.ResolventExamples KomorebiPhysics.UnboundedExamples
open scoped lp
noncomputable section
example : ‖commutator (R 0) P‖ ≤ ‖B‖ / (0 : ℝ)^2 := by
  simp only [zero_parameter_bound_rejected]
end
