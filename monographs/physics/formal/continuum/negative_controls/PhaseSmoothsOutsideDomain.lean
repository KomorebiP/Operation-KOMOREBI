import KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HarmonicSurrogates
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.UnboundedExamples
open scoped Topology lp
noncomputable section
example : evolution harmonicEigenvalue 1 roughState ∈ DiagonalDomain.domain harmonicEigenvalue := by
  rw [domain_iff]
  simp only [roughState_not_domain]
end
