import KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HarmonicSurrogates
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.UnboundedExamples
open scoped Topology lp
noncomputable section
example : roughState ∈ DiagonalDomain.domain harmonicEigenvalue := by
  simp only [roughState_not_domain]
end
