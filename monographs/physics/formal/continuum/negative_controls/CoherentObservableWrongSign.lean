import KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HarmonicSurrogates
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.UnboundedExamples
open scoped Topology lp
noncomputable section
example : HasDerivAt (fun t => ‖coherentAmplitude t‖ ^ 2 / 2) (-12/25) 0 := by
  apply coherent_observable_hasDerivAt.congr_deriv
  norm_num
end
