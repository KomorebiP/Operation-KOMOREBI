/- Intentionally invalid diagnostic. Excluded from production imports. -/
import tests.Contracts
set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesTests
example : ∃ b : ℚ → finiteSupport,
    ∀ r t : ℚ, cocycle (pairedSelector allFalse) r t + b r + b t - b (r+t) = 0 := by
  refine ⟨fun _ => 0, ?_⟩
  intro r t
  simp
