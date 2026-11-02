import GraphQuotient

/-!
Exact cardinality forms of the binary graph ranks. For a finite binary space,
its cardinality dimension is log2 of its size. The exact powers of two below
are proved before taking logarithms; the ranks are not defined by the formulas.
-/

namespace KRS.Graph

variable {n : Nat}

theorem cut_fields_length_pos (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    0 < (cutFields G).length := by
  have hm := (cut_fields_complete G (derivative G (fun _ => false))).mpr
    ⟨fun _ => false, rfl⟩
  cases h : cutFields G with
  | nil => simp [h] at hm
  | cons r rs => simp

theorem component_index_le_vertices (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    {c : Nat} (I : ComponentIndex G c) : c ≤ n := by
  apply (Nat.pow_le_pow_iff_right (by decide : 1 < 2)).mp
  rw [cut_fields_partition G I]
  exact Nat.le_mul_of_pos_left _ (cut_fields_length_pos G)

theorem cut_fields_count (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    {c : Nat} (I : ComponentIndex G c) : (cutFields G).length = 2 ^ (n - c) := by
  have hc := component_index_le_vertices G I
  apply Nat.mul_right_cancel (Nat.pow_pos (by decide : 0 < 2) : 0 < 2 ^ c)
  rw [← cut_fields_partition G I, ← Nat.pow_add]
  congr 1
  omega

theorem quotient_classes_length_pos (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    0 < (quotientClasses G).length := by
  have hm := quotient_classes_complete G (edgeClass G (fun _ => false))
  cases h : quotientClasses G with
  | nil => simp [h] at hm
  | cons r rs => simp

theorem cut_rank_le_edges (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    {c : Nat} (I : ComponentIndex G c) : n - c ≤ edgeCount G := by
  apply (Nat.pow_le_pow_iff_right (by decide : 1 < 2)).mp
  rw [quotient_partition G, cut_fields_count G I]
  exact Nat.le_mul_of_pos_left _ (quotient_classes_length_pos G)

theorem quotient_classes_count (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    {c : Nat} (I : ComponentIndex G c) :
    (quotientClasses G).length = 2 ^ (edgeCount G + c - n) := by
  have hc := component_index_le_vertices G I
  have he := cut_rank_le_edges G I
  apply Nat.mul_right_cancel (Nat.pow_pos (by decide : 0 < 2) : 0 < 2 ^ (n - c))
  have hp := quotient_partition G
  rw [cut_fields_count G I] at hp
  rw [← hp, ← Nat.pow_add]
  congr 1
  omega

def cutRank (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] : Nat :=
  Nat.log2 (cutFields G).length

def quotientRank (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] : Nat :=
  Nat.log2 (quotientClasses G).length

theorem cut_rank_formula (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    {c : Nat} (I : ComponentIndex G c) : cutRank G = n - c := by
  rw [cutRank, cut_fields_count G I, Nat.log2_two_pow]

theorem quotient_rank_formula (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    {c : Nat} (I : ComponentIndex G c) : quotientRank G = edgeCount G + c - n := by
  rw [quotientRank, quotient_classes_count G I, Nat.log2_two_pow]

theorem graph_rank_nullity (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    {c : Nat} (I : ComponentIndex G c) : cutRank G + c = n := by
  rw [cut_rank_formula G I]
  have hc := component_index_le_vertices G I
  omega

theorem graph_quotient_rank_balance (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    {c : Nat} (I : ComponentIndex G c) : quotientRank G + cutRank G = edgeCount G := by
  rw [quotient_rank_formula G I, cut_rank_formula G I]
  have hc := component_index_le_vertices G I
  have he := cut_rank_le_edges G I
  omega

theorem cut_count_by_components (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    (cutFields G).length = 2 ^ (n - componentCount G) :=
  cut_fields_count G (canonicalComponentIndex G)

theorem quotient_count_by_components (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    (quotientClasses G).length = 2 ^ (edgeCount G + componentCount G - n) :=
  quotient_classes_count G (canonicalComponentIndex G)

theorem cut_rank_by_components (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    cutRank G = n - componentCount G := cut_rank_formula G (canonicalComponentIndex G)

theorem quotient_rank_by_components (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    quotientRank G = edgeCount G + componentCount G - n :=
  quotient_rank_formula G (canonicalComponentIndex G)

theorem cut_rank_by_automatic_components (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    cutRank G = n - (buildTraversal G).1 := cut_rank_formula G (buildTraversal G).2.index

theorem quotient_rank_by_automatic_components (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    quotientRank G = edgeCount G + (buildTraversal G).1 - n :=
  quotient_rank_formula G (buildTraversal G).2.index

end KRS.Graph
