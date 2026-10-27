import AVOC.RateDistortionLower
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

namespace Komorebi.AVOC

/-- Three raw states with pairwise value gaps larger than `2` at tolerance `η=1`. -/
def threeLevelValue : Fin 3 → ℚ
  | ⟨0, _⟩ => 0
  | ⟨1, _⟩ => 3
  | ⟨2, _⟩ => 6

/-- The full three-state set is pairwise `2η`-separated for `η=1`. -/
theorem threeLevel_pairwise_separated :
    PairwiseValueSeparated threeLevelValue 1 (Finset.univ : Finset (Fin 3)) := by
  intro s hs t ht hne
  fin_cases s <;> fin_cases t <;> simp_all [threeLevelValue] <;> norm_num

/-- Any one-unit-accurate representation of the three-level value function
requires at least three context codes. -/
theorem threeLevel_requires_three_codes
    {Z : Type*} [Fintype Z] [DecidableEq Z]
    (φ : Fin 3 → Z) (Vbar : Z → ℚ)
    (happrox : ValueApproximation φ threeLevelValue Vbar 1) :
    3 ≤ Fintype.card Z := by
  have h := separated_card_le_code_card φ threeLevelValue Vbar 1
    (Finset.univ : Finset (Fin 3)) happrox threeLevel_pairwise_separated
  simpa using h

end Komorebi.AVOC
