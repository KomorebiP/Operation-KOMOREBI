import RealizationBoundaries
set_option autoImplicit false
noncomputable section
open RealizationBoundaries

example (a : ℕ → Bool) : pairedGroup a ≃ₜ+ Ambient := by
  exact pairedCompletionEquiv a
