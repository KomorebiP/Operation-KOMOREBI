import KomorebiPhysics.ResolventExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.ResolventDomain
open KomorebiPhysics.ResolventExamples KomorebiPhysics.UnboundedExamples
open scoped lp
noncomputable section
example : ∀ x : harmonic.domain, harmonic (restrict harmonic P P_domain x) = P (harmonic x) := by
  simp only [packet_does_not_reduce]
end
