import GraphPinning

/-!
Reconstruction from supplied, checked component-root paths. The executable
solver chooses root values from pins and checks one resulting labeling. It
does not enumerate Boolean vertex assignments. Constructing a traversal from
an arbitrary input graph is a separate algorithmic obligation.
-/

namespace KRS.Graph

structure RootedTraversal {n : Nat} (G : SimpleGraph (Fin n)) (c : Nat) where
  index : ComponentIndex G c
  walk : (v : Fin n) → Walk G (index.vertex (index.label v)) v

variable {n c : Nat} {G : SimpleGraph (Fin n)}

def traversalPotential (T : RootedTraversal G c) (r : Fin n → Fin n → Bool)
    (v : Fin n) : Bool := (T.walk v).integral r

def componentRootValue (T : RootedTraversal G c) (r : Fin n → Fin n → Bool)
    (pins : List (Fin n × Bool)) (i : Fin c) : Bool :=
  match pins.find? (fun pin => T.index.label pin.1 == i) with
  | none => false
  | some pin => Bool.xor pin.2 (traversalPotential T r pin.1)

def traversalCandidate (T : RootedTraversal G c) (r : Fin n → Fin n → Bool)
    (pins : List (Fin n × Bool)) (v : Fin n) : Bool :=
  Bool.xor (componentRootValue T r pins (T.index.label v)) (traversalPotential T r v)

def traversalSolve (T : RootedTraversal G c) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) : Option (Fin n → Bool) :=
  let a := traversalCandidate T r pins
  if checkSolution G r pins a then some a else none

theorem traversal_potential_of_integrates (T : RootedTraversal G c)
    (r : Fin n → Fin n → Bool) (a : Fin n → Bool) (ha : Integrates (G := G) r a)
    (v : Fin n) : traversalPotential T r v = Bool.xor (a (T.index.vertex (T.index.label v))) (a v) :=
  (T.walk v).integral_of_integrates r a ha

theorem component_root_value_at_pin (T : RootedTraversal G c)
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) (a : Fin n → Bool)
    (ha : Integrates (G := G) r a) (hp : PinsMatch a pins)
    (v : Fin n) (b : Bool) (hm : (v, b) ∈ pins) :
    componentRootValue T r pins (T.index.label v) = a (T.index.vertex (T.index.label v)) := by
  unfold componentRootValue
  cases hs : pins.find? (fun pin => T.index.label pin.1 == T.index.label v) with
  | none =>
    have hn := (List.find?_eq_none.mp hs) (v, b) hm
    simp at hn
  | some pin =>
    have hmem := List.mem_of_find?_eq_some hs
    have ht : (T.index.label pin.1 == T.index.label v) = true :=
      List.find?_some (p := fun pin : Fin n × Bool => T.index.label pin.1 == T.index.label v) hs
    have hl := beq_iff_eq.mp ht
    have hv := pins_match_at_vertex a pins hp pin.1 pin.2 hmem
    have hi := traversal_potential_of_integrates T r a ha pin.1
    change Bool.xor pin.2 (traversalPotential T r pin.1) = a (T.index.vertex (T.index.label v))
    rw [← hv, hi, hl]
    cases ap : a pin.1 <;> cases ar : a (T.index.vertex (T.index.label v)) <;> decide

theorem traversal_candidate_integrates (T : RootedTraversal G c)
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool))
    (a : Fin n → Bool) (ha : Integrates (G := G) r a) :
    Integrates (G := G) r (traversalCandidate T r pins) := by
  intro v w h
  have hv := traversal_potential_of_integrates T r a ha v
  have hw := traversal_potential_of_integrates T r a ha w
  rw [ha v w h]
  simp only [traversalCandidate, hv, hw, T.index.edge_same v w h]
  cases componentRootValue T r pins (T.index.label w) <;>
    cases a (T.index.vertex (T.index.label w)) <;> cases a v <;> cases a w <;> decide

theorem traversal_candidate_matches_pins (T : RootedTraversal G c)
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool))
    (a : Fin n → Bool) (ha : Integrates (G := G) r a) (hp : PinsMatch a pins) :
    PinsMatch (traversalCandidate T r pins) pins := by
  apply (pins_match_iff_pointwise _ pins).mpr
  intro v b hm
  have hr := component_root_value_at_pin T r pins a ha hp v b hm
  have hi := traversal_potential_of_integrates T r a ha v
  have hv := pins_match_at_vertex a pins hp v b hm
  simp only [traversalCandidate, hr, hi, hv]
  cases a (T.index.vertex (T.index.label v)) <;> cases b <;> decide

theorem traversal_solve_sound (T : RootedTraversal G c) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) (a : Fin n → Bool)
    (h : traversalSolve T r pins = some a) : Integrates (G := G) r a ∧ PinsMatch a pins := by
  change (if checkSolution G r pins (traversalCandidate T r pins) then
    some (traversalCandidate T r pins) else none) = some a at h
  split at h
  · next hc =>
      cases h
      exact (check_solution_true G r pins _).mp hc
  · contradiction

theorem traversal_solve_of_solution (T : RootedTraversal G c) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool))
    (a : Fin n → Bool) (ha : Integrates (G := G) r a) (hp : PinsMatch a pins) :
    traversalSolve T r pins = some (traversalCandidate T r pins) := by
  have hc := (check_solution_true G r pins _).mpr
    ⟨traversal_candidate_integrates T r pins a ha, traversal_candidate_matches_pins T r pins a ha hp⟩
  simp [traversalSolve, hc]

theorem traversal_solve_complete (T : RootedTraversal G c) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool))
    (a : Fin n → Bool) (ha : Integrates (G := G) r a) (hp : PinsMatch a pins) :
    (traversalSolve T r pins).isSome = true := by
  rw [traversal_solve_of_solution T r pins a ha hp]
  rfl

theorem traversal_solve_none_iff_no_solution (T : RootedTraversal G c) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) :
    traversalSolve T r pins = none ↔ ¬ ∃ a, Integrates (G := G) r a ∧ PinsMatch a pins := by
  constructor
  · intro hn ⟨a, ha, hp⟩
    have hs := traversal_solve_complete T r pins a ha hp
    simp [hn] at hs
  · intro h
    cases hs : traversalSolve T r pins with
    | none => rfl
    | some a => exact False.elim (h ⟨a, traversal_solve_sound T r pins a hs⟩)

theorem traversal_solve_none_iff_reference (T : RootedTraversal G c) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) :
    traversalSolve T r pins = none ↔ solve G r pins = none := by
  rw [traversal_solve_none_iff_no_solution, solve_none_iff_no_solution]

theorem traversal_solve_agrees_on_existence (T : RootedTraversal G c) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) :
    (traversalSolve T r pins).isSome = (solve G r pins).isSome := by
  have h := traversal_solve_none_iff_reference T r pins
  cases ht : traversalSolve T r pins <;> cases hs : solve G r pins <;> simp_all

theorem traversal_solve_unique_when_covered (T : RootedTraversal G c) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) (a b : Fin n → Bool)
    (ha : traversalSolve T r pins = some a) (hb : solve G r pins = some b)
    (cover : ∀ v, ∃ w value, (w, value) ∈ pins ∧ Reachable G v w) : a = b := by
  obtain ⟨hai, hap⟩ := traversal_solve_sound T r pins a ha
  obtain ⟨hbi, hbp⟩ := solve_sound G r pins b hb
  exact pins_cover_unique G r pins a b hai hbi hap hbp cover

end KRS.Graph
