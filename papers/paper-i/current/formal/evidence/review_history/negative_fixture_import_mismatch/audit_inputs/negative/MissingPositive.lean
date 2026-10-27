import PaperICompletion8.SemisimpleExistence
set_option autoImplicit false
example (D : Type) [DivisionRing D] :
    Komorebi.SeedRankBasics.seedRank (Matrix (Fin 0) (Fin 0) D) (Fin 0 → D) = 1 := by
  exact Komorebi.PaperICompletion8.RegularMultiplicity.natural_seedRank_eq_one (Nat.zero_le 0)
