import PaperIRelease.ExactSequences
open Komorebi.PaperIRelease Komorebi.SeedRankBasics
example : seedRank ℤ ℤ ≤ seedRank ℤ (Fin 0 → ℤ) + seedRank ℤ (Fin 0 → ℤ) := by
  apply seedRank_le_add_of_exact (0 : (Fin 0 → ℤ) →ₗ[ℤ] ℤ)
    (0 : ℤ →ₗ[ℤ] (Fin 0 → ℤ))
  · rfl
  · intro y
    exact ⟨0, Subsingleton.elim _ _⟩
