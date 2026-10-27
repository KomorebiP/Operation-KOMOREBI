/- Intentionally invalid diagnostic. Excluded from production imports. -/
import tests.Contracts
set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesTests
example : ∃ y : pairedGroup allFalse,
    (2 : ℕ) • y = markedElement (pairedSelector allFalse) := by
  exact third_root
