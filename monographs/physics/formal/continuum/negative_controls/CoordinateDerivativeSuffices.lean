import KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HarmonicSurrogates
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.UnboundedExamples
open scoped Topology lp
noncomputable section
example : DifferentiableAt ℝ (fun s => evolution harmonicEigenvalue s roughState) 0 := by
  have coordinates := rough_coordinates_differentiable 0
  simp only [rough_orbit_not_differentiable]
end
