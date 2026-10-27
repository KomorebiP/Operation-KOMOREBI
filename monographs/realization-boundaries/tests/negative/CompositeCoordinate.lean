/- Intentionally invalid diagnostic. Excluded from production imports. -/
import tests.Contracts
set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesTests
def compositeCoordinate : Prime := ⟨4, by decide⟩
