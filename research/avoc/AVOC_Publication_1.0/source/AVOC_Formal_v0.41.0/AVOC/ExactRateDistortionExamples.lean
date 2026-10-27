import AVOC.GreedyRateDistortion
import AVOC.RateDistortionExamples
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

namespace Komorebi.AVOC

/-- The previous three-level example has exact scalar context number three at
tolerance one; the v0.9 packing lower bound is attained. -/
theorem threeLevel_exact_code_number :
    exactValueCodeNumber threeLevelValue 1 (by norm_num) = 3 := by
  apply le_antisymm
  · have h := exactValueCodeNumber_le_distinct_value_card
      threeLevelValue 1 (by norm_num)
    exact h
  · have h := separated_card_le_exactValueCodeNumber
      threeLevelValue 1 (by norm_num)
      (Finset.univ : Finset (Fin 3)) threeLevel_pairwise_separated
    simpa using h


/-- The certified greedy algorithm computes the exact three-code optimum. -/
theorem threeLevel_greedy_count :
    greedyPointCoverCount 1 (by norm_num) (Finset.univ.image threeLevelValue) = 3 := by
  rw [greedy_computes_exactValueCodeNumber, threeLevel_exact_code_number]

/-- Four values grouped into two exact radius-`1/2` clusters. -/
def twoClusterValue : Fin 4 → ℚ
  | ⟨0, _⟩ => 0
  | ⟨1, _⟩ => 1
  | ⟨2, _⟩ => 4
  | ⟨3, _⟩ => 5

/-- Two centers suffice for the clustered example. -/
theorem twoCluster_two_center_cover :
    ValueCenterCover twoClusterValue (1 / 2 : ℚ)
      ({(1 / 2 : ℚ), (9 / 2 : ℚ)} : Finset ℚ) := by
  intro s
  fin_cases s
  · exact ⟨1 / 2, by norm_num, by norm_num [twoClusterValue]⟩
  · exact ⟨1 / 2, by norm_num, by norm_num [twoClusterValue]⟩
  · exact ⟨9 / 2, by norm_num, by norm_num [twoClusterValue]⟩
  · exact ⟨9 / 2, by norm_num, by norm_num [twoClusterValue]⟩

/-- Two separated witnesses show that one center cannot suffice. -/
theorem twoCluster_pair_separated :
    PairwiseValueSeparated twoClusterValue (1 / 2 : ℚ)
      ({(0 : Fin 4), (2 : Fin 4)} : Finset (Fin 4)) := by
  intro s hs t ht hne
  fin_cases s <;> fin_cases t <;>
    simp_all [twoClusterValue]

/-- The exact finite rate-distortion number of the clustered example is two. -/
theorem twoCluster_exact_code_number :
    exactValueCodeNumber twoClusterValue (1 / 2 : ℚ) (by norm_num) = 2 := by
  apply le_antisymm
  · have h := exactValueCodeNumber_le_cover_card
      twoClusterValue (1 / 2 : ℚ) (by norm_num)
      ({(1 / 2 : ℚ), (9 / 2 : ℚ)} : Finset ℚ)
      twoCluster_two_center_cover
    norm_num at h ⊢
    exact h
  · have h := separated_card_le_exactValueCodeNumber
      twoClusterValue (1 / 2 : ℚ) (by norm_num)
      ({(0 : Fin 4), (2 : Fin 4)} : Finset (Fin 4))
      twoCluster_pair_separated
    norm_num at h ⊢
    exact h


/-- The greedy recursion also computes the two-cluster optimum exactly. -/
theorem twoCluster_greedy_count :
    greedyPointCoverCount (1 / 2 : ℚ) (by norm_num)
      (Finset.univ.image twoClusterValue) = 2 := by
  rw [greedy_computes_exactValueCodeNumber, twoCluster_exact_code_number]

/-- At tolerance one, the values `0,1,2` collapse exactly to one context code. -/
def oneClusterValue : Fin 3 → ℚ
  | ⟨0, _⟩ => 0
  | ⟨1, _⟩ => 1
  | ⟨2, _⟩ => 2

/-- The midpoint center `1` exactly witnesses one-symbol optimality. -/
theorem oneCluster_exact_code_number :
    exactValueCodeNumber oneClusterValue 1 (by norm_num) = 1 := by
  apply exactValueCodeNumber_eq_one_of_center oneClusterValue 1 (by norm_num) 1
  intro s
  fin_cases s <;> norm_num [oneClusterValue]

end Komorebi.AVOC
