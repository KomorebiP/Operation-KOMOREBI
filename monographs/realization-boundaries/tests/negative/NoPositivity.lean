/- Intentionally invalid diagnostic. Excluded from production imports. -/
import tests.Contracts
set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesTests
example (m : ℕ) : Function.Bijective (fun v : TailSpace => m • v) := by
  exact tail_nsmul_bijective (by omega)
