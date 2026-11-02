import GraphPathSearch

/-!
An automatic traversal constructor and graph reconstruction solver. All
operational choices use finite lists and checked path-table entries. The
correctness proof reuses the supplied-traversal solver's contract.
-/

namespace KRS.Graph

universe u

def listPosition {A : Type u} [DecidableEq A] (l : List A) (a : A) (h : a ∈ l) : Fin l.length :=
  match l with
  | [] => False.elim (List.not_mem_nil h)
  | b :: tail =>
      if heq : a = b then ⟨0, by simp⟩
      else (listPosition tail a ((List.mem_cons.mp h).resolve_left heq)).succ

theorem get_list_position {A : Type u} [DecidableEq A] (l : List A) (a : A) (h : a ∈ l) :
    l.get (listPosition l a h) = a := by
  induction l with
  | nil => simp at h
  | cons b tail ih =>
    by_cases heq : a = b
    · subst a; simp [listPosition]
    · simpa [listPosition, heq] using ih ((List.mem_cons.mp h).resolve_left heq)

theorem list_position_get {A : Type u} [DecidableEq A] (l : List A) (h : l.Nodup)
    (i : Fin l.length) : listPosition l (l.get i) (l.get_mem i) = i :=
  nodup_get_injective l h (get_list_position l (l.get i) (l.get_mem i))

variable {n : Nat} {G : SimpleGraph (Fin n)}

def selectedRoot (P : PathTable G) (v : Fin n) : Fin n :=
  ((finiteVertices n).find? (fun u => (pathAt P u v).isSome)).getD v

theorem selected_root_some (P : PathTable G)
    (hP : ∀ v w, (pathAt P v w).isSome = true ↔ Reachable G v w) (v : Fin n) :
    (finiteVertices n).find? (fun u => (pathAt P u v).isSome) = some (selectedRoot P v) := by
  have hex : ((finiteVertices n).find? (fun u => (pathAt P u v).isSome)).isSome = true :=
    List.find?_isSome.mpr ⟨v, mem_finite_vertices v, (hP v v).mpr ⟨.nil v⟩⟩
  cases hs : (finiteVertices n).find? (fun u => (pathAt P u v).isSome) with
  | none => simp [hs] at hex
  | some u => simp [selectedRoot, hs]

theorem selected_root_path (P : PathTable G)
    (hP : ∀ v w, (pathAt P v w).isSome = true ↔ Reachable G v w) (v : Fin n) :
    (pathAt P (selectedRoot P v) v).isSome = true :=
  List.find?_some (p := fun u => (pathAt P u v).isSome) (selected_root_some P hP v)

theorem selected_root_constant (P : PathTable G)
    (hP : ∀ v w, (pathAt P v w).isSome = true ↔ Reachable G v w)
    (v w : Fin n) (h : Reachable G v w) : selectedRoot P v = selectedRoot P w := by
  obtain ⟨walk⟩ := h
  have heq : (fun u => (pathAt P u v).isSome) = (fun u => (pathAt P u w).isSome) := by
    funext u
    apply Bool.eq_iff_iff.mpr
    rw [hP u v, hP u w]
    constructor
    · rintro ⟨p⟩; exact ⟨p.append walk⟩
    · rintro ⟨p⟩; exact ⟨p.append walk.reverse⟩
  have hv := selected_root_some P hP v
  rw [heq] at hv
  exact Option.some.inj (hv.symm.trans (selected_root_some P hP w))

theorem selected_root_idempotent (P : PathTable G)
    (hP : ∀ v w, (pathAt P v w).isSome = true ↔ Reachable G v w) (v : Fin n) :
    selectedRoot P (selectedRoot P v) = selectedRoot P v :=
  selected_root_constant P hP _ v ((hP _ v).mp (selected_root_path P hP v))

def automaticRoots (P : PathTable G) : List (Fin n) :=
  distinctValues (List.ofFn (selectedRoot P))

theorem automatic_roots_nodup (P : PathTable G) : (automaticRoots P).Nodup :=
  distinct_values_nodup _

theorem selected_root_mem (P : PathTable G) (v : Fin n) : selectedRoot P v ∈ automaticRoots P :=
  (distinct_values_complete _ _).mpr (List.mem_ofFn.mpr ⟨v, rfl⟩)

def automaticRootPosition (P : PathTable G) (v : Fin n) : Fin (automaticRoots P).length :=
  listPosition _ (selectedRoot P v) (selected_root_mem P v)

theorem automatic_root_at_position (P : PathTable G) (v : Fin n) :
    (automaticRoots P).get (automaticRootPosition P v) = selectedRoot P v :=
  get_list_position _ _ _

theorem automatic_root_fixed (P : PathTable G)
    (hP : ∀ v w, (pathAt P v w).isSome = true ↔ Reachable G v w)
    (i : Fin (automaticRoots P).length) :
    selectedRoot P ((automaticRoots P).get i) = (automaticRoots P).get i := by
  have hm := (automaticRoots P).get_mem i
  obtain ⟨v, hv⟩ := List.mem_ofFn.mp ((distinct_values_complete _ _).mp hm)
  rw [← hv]
  exact selected_root_idempotent P hP v

def automaticIndex (P : PathTable G)
    (hP : ∀ v w, (pathAt P v w).isSome = true ↔ Reachable G v w) :
    ComponentIndex G (automaticRoots P).length where
  label := automaticRootPosition P
  vertex := (automaticRoots P).get
  edge_same := by
    intro v w h
    have hr := selected_root_constant P hP v w ⟨.cons h (.nil w)⟩
    simp only [automaticRootPosition, hr]
  vertex_reachable := by
    intro v
    rw [automatic_root_at_position]
    exact (hP _ v).mp (selected_root_path P hP v)
  label_vertex := by
    intro i
    unfold automaticRootPosition
    simpa only [automatic_root_fixed P hP i] using
      list_position_get _ (automatic_roots_nodup P) i

def traversalOfPaths (P : PathTable G)
    (hP : ∀ v w, (pathAt P v w).isSome = true ↔ Reachable G v w) :
    RootedTraversal G (automaticRoots P).length where
  index := automaticIndex P hP
  walk := fun v => by
    change Walk G ((automaticRoots P).get (automaticRootPosition P v)) v
    rw [automatic_root_at_position]
    exact (pathAt P (selectedRoot P v) v).get (selected_root_path P hP v)

def buildTraversal (G : SimpleGraph (Fin n)) [DecidableRel G.Adj] :
    (c : Nat) × RootedTraversal G c :=
  let paths := boundedPaths G n
  ⟨(automaticRoots paths).length, traversalOfPaths paths (bounded_paths_reachable G)⟩

def automaticSolve (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) : Option (Fin n → Bool) :=
  traversalSolve (buildTraversal G).2 r pins

theorem automatic_solve_sound (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) (a : Fin n → Bool)
    (h : automaticSolve G r pins = some a) : Integrates (G := G) r a ∧ PinsMatch a pins :=
  traversal_solve_sound (buildTraversal G).2 r pins a h

theorem automatic_solve_complete (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool))
    (a : Fin n → Bool) (ha : Integrates (G := G) r a) (hp : PinsMatch a pins) :
    (automaticSolve G r pins).isSome = true :=
  traversal_solve_complete (buildTraversal G).2 r pins a ha hp

theorem automatic_solve_none_iff_no_solution (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) :
    automaticSolve G r pins = none ↔ ¬ ∃ a, Integrates (G := G) r a ∧ PinsMatch a pins :=
  traversal_solve_none_iff_no_solution (buildTraversal G).2 r pins

theorem automatic_solve_agrees_on_existence (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) :
    (automaticSolve G r pins).isSome = (solve G r pins).isSome :=
  traversal_solve_agrees_on_existence (buildTraversal G).2 r pins

theorem automatic_solve_unique_when_covered (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) (a b : Fin n → Bool)
    (ha : automaticSolve G r pins = some a) (hb : solve G r pins = some b)
    (cover : ∀ v, ∃ w value, (w, value) ∈ pins ∧ Reachable G v w) : a = b :=
  traversal_solve_unique_when_covered (buildTraversal G).2 r pins a b ha hb cover

end KRS.Graph
