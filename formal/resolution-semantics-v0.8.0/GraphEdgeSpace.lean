import GraphAutomaticTraversal
import GraphFiniteCounting

/-!
Each undirected edge is indexed exactly once, by its increasing endpoint pair.
The derivative and its actual image are finite binary spaces.
-/

namespace KRS.Graph

variable {n : Nat}

instance bitDecidableEq (k : Nat) : DecidableEq (Fin k → Bool) := fun a b =>
  if h : ∀ i, a i = b i then isTrue (funext h)
  else isFalse (fun heq => h (congrFun heq))

def edgeList (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] : List (Fin n × Fin n) :=
  distinctValues ((finiteVertices n).flatMap (fun v =>
    ((finiteVertices n).map (fun w => (v, w))).filter
      (fun e => decide (e.1 < e.2 ∧ G.Adj e.1 e.2))))

theorem edge_list_nodup (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    (edgeList G).Nodup := distinct_values_nodup _

theorem edge_list_mem (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] (v w : Fin n) :
    (v, w) ∈ edgeList G ↔ v < w ∧ G.Adj v w := by
  simp [edgeList, distinct_values_complete, List.mem_flatMap, finiteVertices]

def edgeCount (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] : Nat := (edgeList G).length

abbrev EdgeBits (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] := Fin (edgeCount G) → Bool

def derivative (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] (a : Fin n → Bool) :
    EdgeBits G :=
  let edges := edgeList G
  fun i => let e := edges.get i; Bool.xor (a e.1) (a e.2)

def bitXor {k : Nat} (a b : Fin k → Bool) : Fin k → Bool := fun i => Bool.xor (a i) (b i)

theorem bit_xor_self {k : Nat} (a : Fin k → Bool) : bitXor a a = fun _ => false := by
  funext i
  simp [bitXor]

theorem bit_xor_zero {k : Nat} (a : Fin k → Bool) : bitXor a (fun _ => false) = a := by
  funext i
  simp [bitXor]

theorem bit_xor_comm {k : Nat} (a b : Fin k → Bool) : bitXor a b = bitXor b a := by
  funext i
  exact Bool.xor_comm _ _

theorem bit_xor_assoc {k : Nat} (a b c : Fin k → Bool) :
    bitXor (bitXor a b) c = bitXor a (bitXor b c) := by
  funext i
  exact Bool.xor_assoc _ _ _

theorem bit_xor_cancel {k : Nat} (a b : Fin k → Bool) : bitXor a (bitXor a b) = b := by
  funext i
  simp only [bitXor]
  cases a i <;> cases b i <;> rfl

theorem derivative_zero (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    derivative G (fun _ => false) = fun _ => false := by
  funext i
  rfl

theorem derivative_xor (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] (a b : Fin n → Bool) :
    derivative G (bitXor a b) = bitXor (derivative G a) (derivative G b) := by
  funext i
  simp only [derivative, bitXor]
  cases a ((edgeList G).get i).1 <;> cases a ((edgeList G).get i).2 <;>
    cases b ((edgeList G).get i).1 <;> cases b ((edgeList G).get i).2 <;> rfl

theorem derivative_eq_iff (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (a b : Fin n → Bool) :
    derivative G a = derivative G b ↔
      Integrates (G := G) (fun v w => Bool.xor (b v) (b w)) a := by
  constructor
  · intro h v w hvw
    have getEdge (v w : Fin n) (ho : v < w) (he : G.Adj v w) :
        Bool.xor (a v) (a w) = Bool.xor (b v) (b w) := by
      obtain ⟨i, hi⟩ := List.mem_iff_get.mp ((edge_list_mem G v w).mpr ⟨ho, he⟩)
      have hh := congrFun h i
      simpa only [derivative, hi] using hh
    have hne : v ≠ w := by intro heq; subst w; exact G.loopless v hvw
    by_cases hlt : v < w
    · exact (getEdge v w hlt hvw).symm
    · have hgt : w < v := by omega
      simpa only [Bool.xor_comm] using (getEdge w v hgt (G.symm hvw)).symm
  · intro h
    funext i
    have hm := (edge_list_mem G _ _).mp ((edgeList G).get_mem i)
    exact (h _ _ hm.2).symm

def cutFields (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] : List (EdgeBits G) :=
  distinctValues ((assignments n).map (derivative G))

theorem cut_fields_nodup (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    (cutFields G).Nodup := distinct_values_nodup _

theorem cut_fields_complete (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] (r : EdgeBits G) :
    r ∈ cutFields G ↔ ∃ a, derivative G a = r := by
  simp [cutFields, distinct_values_complete, assignments_complete]

theorem derivative_fiber_count (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    {c : Nat} (I : ComponentIndex G c) (r : EdgeBits G) (hr : r ∈ cutFields G) :
    ((assignments n).filter (fun a => derivative G a == r)).length = 2 ^ c := by
  obtain ⟨a, rfl⟩ := (cut_fields_complete G r).mp hr
  have heq : (assignments n).filter (fun b => derivative G b == derivative G a) =
      allSolutions G (fun v w => Bool.xor (a v) (a w)) := by
    apply List.filter_congr
    intro b _
    apply Bool.eq_iff_iff.mpr
    simp [beq_iff_eq, derivative_eq_iff, check_solution_true, PinsMatch]
  rw [heq]
  apply all_solutions_count G I
  exact ⟨a, fun _ _ _ => rfl⟩

theorem cut_fields_partition (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    {c : Nat} (I : ComponentIndex G c) :
    2 ^ n = (cutFields G).length * 2 ^ c := by
  rw [← assignments_length]
  apply constant_fiber_count _ _ (derivative G) (cut_fields_nodup G)
  · intro a _
    exact (cut_fields_complete G _).mpr ⟨a, rfl⟩
  · exact derivative_fiber_count G I

end KRS.Graph
