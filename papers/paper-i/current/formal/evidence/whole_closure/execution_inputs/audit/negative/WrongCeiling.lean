-- Deliberate negative control: ceil(5/2) is3, not2.
import PaperICompletion8.RegularMultiplicity
import Mathlib.Algebra.Quaternion
set_option autoImplicit false
example : Komorebi.SeedRankBasics.seedRank
    (Matrix (Fin 2) (Fin 2) (Quaternion ℚ)) (Fin 5 → Fin 2 → Quaternion ℚ) = 2 := by
  have correct : Komorebi.SeedRankBasics.seedRank
      (Matrix (Fin 2) (Fin 2) (Quaternion ℚ)) (Fin 5 → Fin 2 → Quaternion ℚ) = 3 := by
    simpa [Nat.ceilDiv_eq_add_pred_div] using
      Komorebi.PaperICompletion8.RegularMultiplicity.naturalCopies_seedRank
        (D := Quaternion ℚ) 2 5 (by decide)
  exact correct
