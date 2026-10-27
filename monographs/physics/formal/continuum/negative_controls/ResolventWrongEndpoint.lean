import KomorebiPhysics.SpectralErrorBounds
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.SpectralTruncation
open KomorebiPhysics.HarmonicSurrogates KomorebiPhysics.AnchoredSurrogates
open KomorebiPhysics.SpectralErrorBounds KomorebiPhysics.UnboundedExamples Filter
open scoped Topology lp
noncomputable section
example : ‖diagonal (resolventSymbol 0) - diagonal (truncate (resolventSymbol 0) 10)‖ = 1/10 := by
  rw [resolvent_error_at_ten]
end
