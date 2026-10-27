import PaperICompletion
open Komorebi.PaperICompletion.CyclicClassification
open Komorebi.SingleOperatorGraph
-- EXPECTED REJECTION: the rank-one theorem requires a nonzero space.
example : Komorebi.SeedRankBasics.seedRank
    (operatorAlgebra (0 : Module.End ℚ (Fin 0 → ℚ))) (Fin 0 → ℚ) = 1 := by
  apply (operatorAlgebra_seedRank_eq_one_iff_minpoly_eq_charpoly (0 : Module.End ℚ (Fin 0 → ℚ))).mpr
  simp
