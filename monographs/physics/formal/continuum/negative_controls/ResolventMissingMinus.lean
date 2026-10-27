import KomorebiPhysics.ResolventExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.ResolventDomain
open KomorebiPhysics.ResolventExamples KomorebiPhysics.UnboundedExamples
open scoped lp
noncomputable section
example : commutator (R 0) P = R 0 * B * R 0 := by
  simp only [wrong_sign_rejected]
end
