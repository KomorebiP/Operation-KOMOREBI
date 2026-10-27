/- Intentionally invalid diagnostic. Excluded from production imports. -/
import tests.Contracts
set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesClassificationTests
example : (tailExceptions 0 (0 : finiteSupport)).Finite :=
  tailExceptions_finite (by decide) 0
