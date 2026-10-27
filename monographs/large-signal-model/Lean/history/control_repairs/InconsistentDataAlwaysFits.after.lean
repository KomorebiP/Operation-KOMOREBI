import KomorebiLSM.Block9Examples

example : ∃ B : ℚ →ₗ[ℚ] ℚ, B.comp (0 : ℚ →ₗ[ℚ] ℚ) = LinearMap.id := by
  exact ⟨0, by ext; simp⟩
