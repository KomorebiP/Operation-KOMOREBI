import KomorebiPhysics.ResolventExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.ResolventDomain
open KomorebiPhysics.ResolventExamples KomorebiPhysics.UnboundedExamples
open scoped lp
noncomputable section
example : ‖commutator (R 1) P‖ ^ 2 = 0 := by
  rw [unit_parameter_norm_sq]
  norm_num
end
