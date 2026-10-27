import KomorebiPhysics.SpectralErrorBounds
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.SpectralTruncation
open KomorebiPhysics.HarmonicSurrogates KomorebiPhysics.AnchoredSurrogates
open KomorebiPhysics.SpectralErrorBounds KomorebiPhysics.UnboundedExamples Filter
open scoped Topology lp
noncomputable section
example (M : ℕ) : ‖diagonal (heatSymbol 0 le_rfl) - diagonal (truncate (heatSymbol 0 le_rfl) M)‖ = 0 := by
  rw [heat_zero_error]
