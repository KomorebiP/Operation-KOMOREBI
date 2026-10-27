/- Intentionally invalid diagnostic. Excluded from production imports. -/
import tests.Contracts
set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesClassificationTests
example (S : Set Prime) (x : selectorGroup S) (hx : x.val ∉ finiteSupport) :
    ∀ p, HasPrimeRoot x p ↔ p ∉ S := by
  exact selector_tail_signature S x hx
