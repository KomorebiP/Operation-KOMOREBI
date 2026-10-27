/- Intentionally invalid diagnostic. Excluded from production imports. -/
import tests.Contracts
set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesClassificationTests
example (a b : ℕ → Bool) (e : pairedGroup a ≃+ pairedGroup b) : a = b := by
  exact finite_disagreement_of_pairedEquiv a b e
