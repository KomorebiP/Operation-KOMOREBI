import GraphRanks
import GraphCountExamples
import GraphAutomaticExamples

namespace KRS.Graph.RankExamples

open KRS.Graph.Examples KRS.Graph.CountExamples KRS.Graph.AutomaticExamples

def completeFour : SimpleGraph (Fin 4) where
  Adj := fun u v => u ≠ v
  symm := Ne.symm
  loopless := fun _ h => h rfl

instance completeFourDecidable : DecidableRel completeFour.Adj :=
  fun u v => inferInstanceAs (Decidable (u ≠ v))

def triangleIsolated : SimpleGraph (Fin 4) where
  Adj := fun u v => u.val < 3 ∧ v.val < 3 ∧ u ≠ v
  symm := fun ⟨hu, hv, h⟩ => ⟨hv, hu, Ne.symm h⟩
  loopless := fun _ ⟨_, _, h⟩ => h rfl

instance triangleIsolatedDecidable : DecidableRel triangleIsolated.Adj :=
  fun u v => inferInstanceAs (Decidable (u.val < 3 ∧ v.val < 3 ∧ u ≠ v))

def twoTriangles : SimpleGraph (Fin 6) where
  Adj := fun u v => u.val / 3 = v.val / 3 ∧ u ≠ v
  symm := fun ⟨h, hn⟩ => ⟨h.symm, Ne.symm hn⟩
  loopless := fun _ ⟨_, h⟩ => h rfl

instance twoTrianglesDecidable : DecidableRel twoTriangles.Adj :=
  fun u v => inferInstanceAs (Decidable (u.val / 3 = v.val / 3 ∧ u ≠ v))

theorem edgeless_cut_rank (n : Nat) : cutRank (edgeless n) = 0 := by
  simpa using cut_rank_formula (edgeless n) (edgelessIndex n)

theorem edgeless_quotient_rank (n : Nat) : quotientRank (edgeless n) = 0 := by
  have he : edgeCount (edgeless n) = 0 := by
    cases h : edgeList (edgeless n) with
    | nil => simp [edgeCount, h]
    | cons e es =>
      have hm := (edge_list_mem (edgeless n) e.1 e.2).mp (by simp [h])
      exact hm.2.elim
  simpa [he] using quotient_rank_formula (edgeless n) (edgelessIndex n)

theorem diamond_cut_rank : cutRank diamond = 3 := cut_rank_formula diamond diamondIndex

theorem triangle_quotient_rank : quotientRank triangle = 1 := by
  have he : edgeCount triangle = 3 := by decide
  simpa [he] using quotient_rank_formula triangle triangleIndex

def summary {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] : String :=
  let cuts := (cutFields G).length
  let classes := (quotientClasses G).length
  "n=" ++ toString n ++ ",m=" ++ toString (edgeCount G) ++
  ",c=" ++ toString (buildTraversal G).1 ++
  ",cuts=" ++ toString cuts ++ ",classes=" ++ toString classes ++
  ",rank=" ++ toString (Nat.log2 cuts) ++ ",quotient=" ++ toString (Nat.log2 classes)

def report : List (String × String) := [
  ("rank-empty", summary (edgeless 0)),
  ("rank-isolated", summary (edgeless 1)),
  ("rank-four-isolated", summary (edgeless 4)),
  ("rank-single-edge", summary (lineGraph 2)),
  ("rank-line-four", summary (lineGraph 4)),
  ("rank-triangle", summary triangle),
  ("rank-diamond", summary diamond),
  ("rank-disconnected", summary disconnected),
  ("rank-complete-four", summary completeFour),
  ("rank-triangle-isolated", summary triangleIsolated),
  ("rank-two-triangles", summary twoTriangles)
]

end KRS.Graph.RankExamples
