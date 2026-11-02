import GraphReconstruction

/-!
An exhaustive finite reference solver. The completeness theorem proves that
the search enumerates every binary labeling; the examples do not supply the
general correctness argument. Root pins are arbitrary input constraints.
-/

namespace KRS.Graph

def extend {n : Nat} (bit : Bool) (tail : Fin n → Bool) (v : Fin (n + 1)) : Bool :=
  Fin.cases bit tail v

def assignments : (n : Nat) → List (Fin n → Bool)
  | 0 => [fun v => Fin.elim0 v]
  | n + 1 => (assignments n).map (extend false) ++
      (assignments n).map (extend true)

theorem assignments_complete (n : Nat) (a : Fin n → Bool) : a ∈ assignments n := by
  induction n with
  | zero =>
    change a ∈ [fun v => Fin.elim0 v]
    apply List.mem_singleton.mpr
    funext v
    exact Fin.elim0 v
  | succ n ih =>
    let tail : Fin n → Bool := fun v => a v.succ
    change a ∈ (assignments n).map (extend false) ++
      (assignments n).map (extend true)
    apply List.mem_append.mpr
    cases h : a 0 with
    | false =>
      left
      apply List.mem_map.mpr
      refine ⟨tail, ih tail, ?_⟩
      funext v
      refine Fin.cases ?_ (fun v => ?_) v
      · exact h.symm
      · rfl
    | true =>
      right
      apply List.mem_map.mpr
      refine ⟨tail, ih tail, ?_⟩
      funext v
      refine Fin.cases ?_ (fun v => ?_) v
      · exact h.symm
      · rfl

def PinsMatch {n : Nat} (a : Fin n → Bool) (pins : List (Fin n × Bool)) : Prop :=
  pins.all (fun pin => a pin.1 == pin.2) = true

instance integratesDecidable {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (a : Fin n → Bool) : Decidable (Integrates (G := G) r a) :=
  inferInstanceAs (Decidable (∀ v w, G.Adj v w → r v w = Bool.xor (a v) (a w)))

def checkSolution {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) (a : Fin n → Bool) : Bool :=
  decide (Integrates (G := G) r a) && pins.all (fun pin => a pin.1 == pin.2)

theorem check_solution_true {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) (a : Fin n → Bool) :
    checkSolution G r pins a = true ↔ Integrates (G := G) r a ∧ PinsMatch a pins := by
  simp [checkSolution, PinsMatch]

def solve {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) : Option (Fin n → Bool) :=
  (assignments n).find? (checkSolution G r pins)

theorem solve_sound {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) (a : Fin n → Bool)
    (h : solve G r pins = some a) : Integrates (G := G) r a ∧ PinsMatch a pins :=
  (check_solution_true G r pins a).mp (List.find?_some h)

theorem solve_complete {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) (a : Fin n → Bool)
    (ha : Integrates (G := G) r a) (hp : PinsMatch a pins) :
    (solve G r pins).isSome = true := by
  apply List.find?_isSome.mpr
  exact ⟨a, assignments_complete n a, (check_solution_true G r pins a).mpr ⟨ha, hp⟩⟩

theorem solve_none_iff_no_solution {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) :
    solve G r pins = none ↔ ¬ ∃ a, Integrates (G := G) r a ∧ PinsMatch a pins := by
  constructor
  · intro hn ⟨a, ha, hp⟩
    have hi := solve_complete G r pins a ha hp
    simp [hn] at hi
  · intro h
    cases hs : solve G r pins with
    | none => rfl
    | some a => exact False.elim (h ⟨a, solve_sound G r pins a hs⟩)

theorem solve_exists_iff_cycle_zero {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (hr : ∀ v w, G.Adj v w → r v w = r w v) :
    (solve G r []).isSome = true ↔ CycleZero (G := G) r := by
  constructor
  · intro h
    cases hs : solve G r [] with
    | none => simp [hs] at h
    | some a => exact (integrable_iff_cycle_zero r hr).mp ⟨a, (solve_sound G r [] a hs).1⟩
  · intro hc
    exact solve_complete G r [] (reconstruct G r) (reconstruct_integrates r hr hc) rfl

theorem pins_match_at_vertex {n : Nat} (a : Fin n → Bool) (pins : List (Fin n × Bool))
    (hp : PinsMatch a pins) (v : Fin n) (b : Bool) (hm : (v, b) ∈ pins) : a v = b := by
  exact beq_iff_eq.mp (List.all_eq_true.mp hp (v, b) hm)

theorem pins_cover_unique {n : Nat} (G : SimpleGraph (Fin n))
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) (a b : Fin n → Bool)
    (ha : Integrates (G := G) r a) (hb : Integrates (G := G) r b)
    (hpa : PinsMatch a pins) (hpb : PinsMatch b pins)
    (cover : ∀ v, ∃ w value, (w, value) ∈ pins ∧ Reachable G v w) : a = b := by
  funext v
  obtain ⟨w, value, hm, ⟨p⟩⟩ := cover v
  have haw := pins_match_at_vertex a pins hpa w value hm
  have hbw := pins_match_at_vertex b pins hpb w value hm
  have hi := p.integral_of_integrates r a ha
  have hj := p.integral_of_integrates r b hb
  rw [hi, haw, hbw] at hj
  cases av : a v <;> cases bv : b v <;> cases value <;> simp_all

end KRS.Graph
