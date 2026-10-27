/- Intentionally invalid diagnostic. Excluded from production imports. -/
import tests.Contracts
set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesTests
example : undeclaredBoundaryVariable = undeclaredBoundaryVariable := by rfl
