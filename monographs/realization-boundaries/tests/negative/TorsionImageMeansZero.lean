/- Intentionally invalid diagnostic. Excluded from production imports. -/
import tests.Contracts
set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesClassificationTests
example (f : pairedGroup zeroBits →+ pairedGroup oneBits) (x : pairedGroup zeroBits) : f x = 0 := by
  exact hom_image_finiteSupport _ _ constant_selectors_infinite_disagreement f x
