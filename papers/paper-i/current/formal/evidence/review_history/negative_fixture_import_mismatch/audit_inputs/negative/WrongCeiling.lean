import BoundaryConsumers
example : Komorebi.SeedRankBasics.seedRank
    (Matrix (Fin 2) (Fin 2) PaperIBlock08Tests.H) (Fin 5 → Fin 2 → PaperIBlock08Tests.H) = 2 := by
  exact PaperIBlock08Tests.quaternion_five_copies_rank_three
