/- Intentionally invalid diagnostic. Excluded from production imports. -/
import tests.Contracts
set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesClassificationTests
example : Nonempty (pairedGroup zeroBits ≃+ pairedGroup oneBits) := by
  exact ⟨pairedCommonCompletionEquiv zeroBits oneBits⟩
