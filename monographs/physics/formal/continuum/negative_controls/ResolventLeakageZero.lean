import KomorebiPhysics.ResolventExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.ResolventDomain
open KomorebiPhysics.ResolventExamples KomorebiPhysics.UnboundedExamples
open scoped lp
noncomputable section
example : commutator (R 1) P = 0 := by
  simp only [resolvent_commutator_nonzero]
end
