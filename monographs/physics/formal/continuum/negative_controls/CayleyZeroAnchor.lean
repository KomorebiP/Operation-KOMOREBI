import KomorebiPhysics.SpectralErrorBounds
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.SpectralTruncation
open KomorebiPhysics.HarmonicSurrogates KomorebiPhysics.AnchoredSurrogates
open KomorebiPhysics.SpectralErrorBounds KomorebiPhysics.UnboundedExamples Filter
open scoped Topology lp
noncomputable section
example (M : ℕ) : ‖diagonal cayleySymbol - diagonal (truncate cayleySymbol M)‖ = 0 := by
  rw [cayley_zero_padded_exact]
end
