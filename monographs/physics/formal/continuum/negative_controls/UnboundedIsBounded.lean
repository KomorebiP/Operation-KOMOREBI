import KomorebiPhysics.UnboundedExamples
open scoped lp
open KomorebiPhysics.UnboundedExamples
-- False: boundedness cannot be inferred from unbounded self-adjointness.
example : ∃ C : ℝ, ∀ x : harmonic.domain,
    ‖harmonic x‖ ≤ C * ‖(x : ℓ²(ℕ, ℂ))‖ := by
  simp only [harmonic_unbounded]
