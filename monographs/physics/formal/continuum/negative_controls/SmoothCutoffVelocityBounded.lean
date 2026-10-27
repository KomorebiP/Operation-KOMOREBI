import KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HarmonicSurrogates
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.UnboundedExamples
open scoped Topology lp
noncomputable section
example : ‖deriv (fun s => SpectralTruncation.cutoff 4
    (evolution harmonicEigenvalue s roughState)) 0‖ ^ 2 ≤ 1 := by
  rw [rough_cutoff_velocity_norm_sq]
  norm_num
end
