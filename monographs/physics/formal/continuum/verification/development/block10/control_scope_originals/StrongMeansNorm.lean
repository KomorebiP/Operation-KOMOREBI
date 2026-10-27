import KomorebiPhysics.SpectralErrorBounds
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.SpectralTruncation
open KomorebiPhysics.HarmonicSurrogates KomorebiPhysics.AnchoredSurrogates
open KomorebiPhysics.SpectralErrorBounds KomorebiPhysics.UnboundedExamples Filter
open scoped Topology lp
noncomputable section
example : ‖ContinuousLinearMap.id ℂ Space - cutoff 7‖ = 0 := by
  rw [identity_cutoff_norm_error]
