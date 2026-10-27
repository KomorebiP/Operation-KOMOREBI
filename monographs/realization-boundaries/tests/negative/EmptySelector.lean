/- Intentionally invalid diagnostic. Excluded from production imports. -/
import tests.Contracts
set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesTests
example : Function.Injective (normalEvaluate ∅) := by
  exact (normalEvaluate_bijective (by simp)).1
