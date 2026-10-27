import BoundaryConsumers
open Komorebi.PaperICompletion8.DivisionProduct Komorebi.PaperICompletion8.RegularMultiplicity
open PaperIBlock08Tests
example : Komorebi.SeedRankBasics.seedRank
    (DivisionProductAlgebra (D := MixedD) dims) (MultiplicityModule (D := MixedD) dims mults) = 3 := by
  exact mixed_product_rank_max_not_sum
