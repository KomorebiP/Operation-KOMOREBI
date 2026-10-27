import PaperICompletion3
open Polynomial Komorebi.SeedRankBasics
open Komorebi.PaperICompletion3.InvariantFactorCount
-- Positive degrees alone do not force the factor count to be the seed rank.
example (f : Fin 2 → ℚ[X]) (hf : ∀ i, 0 < (f i).natDegree) :
    IsLeast {n : ℕ | ∃ s : Fin n → ((i : Fin 2) → ℚ[X] ⧸ Ideal.span {f i}),
      FamilyGenerates ℚ[X] ((i : Fin 2) → ℚ[X] ⧸ Ideal.span {f i}) s} 2 := by
  apply invariantFactorProduct_seedNumber_isLeast f hf
  intro i j _
  exact (id (α := f i ∣ f j)) (dvd_refl (f i))
