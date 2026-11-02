import KRSCore

/-!
Binary graph integration and reconstruction.
The cycle condition is stated on simple cycles; the walk normalization proof
derives the condition on all closed walks. Component representatives use
classical choice. The separate finite solver is executable.
-/

namespace KRS.Graph

universe u

structure SimpleGraph (V : Type u) where
  Adj : V → V → Prop
  symm : ∀ {v w}, Adj v w → Adj w v
  loopless : ∀ v, ¬ Adj v v

variable {V : Type u} {G : SimpleGraph V}

inductive Walk (G : SimpleGraph V) : V → V → Type u
  | nil (v : V) : Walk G v v
  | cons {v w z : V} (edge : G.Adj v w) (tail : Walk G w z) : Walk G v z

def Walk.starts {v w : V} : Walk G v w → List V
  | .nil _ => []
  | .cons (v := v) _ tail => v :: tail.starts

def Walk.vertices {v w : V} (p : Walk G v w) : List V := p.starts ++ [w]

def Walk.length {v w : V} : Walk G v w → Nat
  | .nil _ => 0
  | .cons _ tail => tail.length + 1

def Walk.append {v w z : V} : Walk G v w → Walk G w z → Walk G v z
  | .nil _, q => q
  | .cons h p, q => .cons h (p.append q)

def Walk.integral (r : V → V → Bool) {v w : V} : Walk G v w → Bool
  | .nil _ => false
  | .cons (v := v) (w := w) _ tail => Bool.xor (r v w) (tail.integral r)

def Integrates (r : V → V → Bool) (a : V → Bool) : Prop :=
  ∀ v w, G.Adj v w → r v w = Bool.xor (a v) (a w)

def CycleZero (r : V → V → Bool) : Prop :=
  ∀ v (p : Walk G v v), 3 ≤ p.length → p.starts.Nodup → p.integral r = false

theorem Walk.integral_append (r : V → V → Bool) {v w z : V}
    (p : Walk G v w) (q : Walk G w z) :
    (p.append q).integral r = Bool.xor (p.integral r) (q.integral r) := by
  induction p with
  | nil => simp [Walk.append, Walk.integral]
  | cons h p ih => simp [Walk.append, Walk.integral, ih]

theorem Walk.starts_append {v w z : V} (p : Walk G v w) (q : Walk G w z) :
    (p.append q).starts = p.starts ++ q.starts := by
  induction p with
  | nil => rfl
  | cons h p ih => simp [Walk.append, Walk.starts, ih]

theorem Walk.vertices_cons {v w z : V} (h : G.Adj v w) (p : Walk G w z) :
    (Walk.cons h p).vertices = v :: p.vertices := by
  simp [Walk.vertices, Walk.starts]

theorem Walk.start_mem {v w : V} (p : Walk G v w) : v ∈ p.vertices := by
  cases p with
  | nil => simp [Walk.vertices, Walk.starts]
  | cons h p => simp [Walk.vertices_cons]

theorem Walk.split_mem {v w z : V} (p : Walk G v w) (hz : z ∈ p.vertices) :
    ∃ q : Walk G v z, ∃ s : Walk G z w, p = q.append s := by
  induction p with
  | nil v =>
    have heq : z = v := by simpa [Walk.vertices, Walk.starts] using hz
    subst z
    exact ⟨.nil v, .nil v, rfl⟩
  | @cons v x w h p ih =>
    have hm : z = v ∨ z ∈ p.vertices := by simpa [Walk.vertices_cons] using hz
    rcases hm with heq | hm
    · subst z
      exact ⟨.nil v, .cons h p, rfl⟩
    · obtain ⟨q, s, heq⟩ := ih hm
      exact ⟨.cons h q, s, by simp [Walk.append, heq]⟩

theorem Walk.integral_of_integrates (r : V → V → Bool) (a : V → Bool)
    (ha : Integrates (G := G) r a) {v w : V} (p : Walk G v w) :
    p.integral r = Bool.xor (a v) (a w) := by
  induction p with
  | nil => simp [Walk.integral]
  | cons h p ih =>
    rw [Walk.integral, ha _ _ h, ih]
    cases a _ <;> cases a _ <;> cases a _ <;> decide

theorem Walk.simple_prefix {v w z : V} (p : Walk G v w) (q : Walk G w z)
    (hs : (p.append q).vertices.Nodup) : p.vertices.Nodup := by
  have heq : (p.append q).vertices = p.starts ++ q.vertices := by
    simp [Walk.vertices, Walk.starts_append, List.append_assoc]
  rw [heq] at hs
  have hu : w ∈ q.vertices := q.start_mem
  simp only [List.nodup_append] at hs
  rcases hs with ⟨hp, hq, hd⟩
  change (p.starts ++ [w]).Nodup
  apply List.nodup_append.mpr
  refine ⟨hp, by simp, ?_⟩
  intro x hx y hy
  have heq : y = w := by simpa using hy
  subst y
  exact hd x hx w hu

theorem Walk.simple_suffix {v w z : V} (p : Walk G v w) (q : Walk G w z)
    (hs : (p.append q).vertices.Nodup) : q.vertices.Nodup := by
  have heq : (p.append q).vertices = p.starts ++ q.vertices := by
    simp [Walk.vertices, Walk.starts_append, List.append_assoc]
  rw [heq] at hs
  exact (List.nodup_append.mp hs).2.1

theorem Walk.simple_closed_cons {v w : V} (h : G.Adj v w) (p : Walk G w v)
    (hp : p.vertices.Nodup) : (Walk.cons h p).starts.Nodup := by
  have hv : v ∉ p.starts := by
    have hn := List.nodup_append.mp hp
    intro hm
    exact hn.2.2 v hm v (by simp) rfl
  have hn := (List.nodup_append.mp hp).1
  simpa [Walk.starts] using List.nodup_cons.mpr ⟨hv, hn⟩

theorem Walk.short_closed_zero (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v)
    {v : V} (p : Walk G v v) (hl : p.length < 3) : p.integral r = false := by
  cases p with
  | nil => rfl
  | @cons v w v h p =>
    cases p with
    | nil => exact False.elim (G.loopless v h)
    | @cons w z v h2 p =>
      cases p with
      | nil => simp [Walk.integral, hr v w h]
      | cons h3 p => simp only [Walk.length] at hl; omega

theorem Walk.simple_closed_zero (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v)
    (hc : CycleZero (G := G) r) {v : V} (p : Walk G v v)
    (hs : p.starts.Nodup) : p.integral r = false := by
  by_cases hl : 3 ≤ p.length
  · exact hc v p hl hs
  · exact p.short_closed_zero r hr (by omega)

-- Erase a zero-sum initial circuit whenever the new start vertex repeats.
theorem Walk.simple_representative (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v)
    (hc : CycleZero (G := G) r) {v w : V} (p : Walk G v w) :
    ∃ q : Walk G v w, q.vertices.Nodup ∧ q.integral r = p.integral r := by
  classical
  induction p with
  | nil v => exact ⟨.nil v, by simp [Walk.vertices, Walk.starts], rfl⟩
  | @cons v x w h p ih =>
    obtain ⟨q, hq, hi⟩ := ih
    by_cases hv : v ∈ q.vertices
    · obtain ⟨front, suffix, heq⟩ := q.split_mem hv
      subst q
      have hp := Walk.simple_prefix front suffix hq
      have hs := Walk.simple_suffix front suffix hq
      have hz := (Walk.cons h front).simple_closed_zero r hr hc
        (Walk.simple_closed_cons h front hp)
      refine ⟨suffix, hs, ?_⟩
      rw [Walk.integral, ← hi, Walk.integral_append]
      have hb : r v x = front.integral r := by
        have hz' : Bool.xor (r v x) (front.integral r) = false := hz
        cases he : r v x <;> cases hp' : front.integral r <;> simp_all
      rw [hb]
      cases front.integral r <;> cases suffix.integral r <;> decide
    · exact ⟨.cons h q, by simpa [Walk.vertices_cons] using List.nodup_cons.mpr ⟨hv, hq⟩,
        by simp [Walk.integral, hi]⟩

theorem Walk.closed_zero_of_cycle_zero (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v)
    (hc : CycleZero (G := G) r) {v : V} (p : Walk G v v) :
    p.integral r = false := by
  obtain ⟨q, hq, hi⟩ := p.simple_representative r hr hc
  cases q with
  | nil => exact hi.symm
  | @cons v w v h q =>
    have hn : v ∉ q.vertices := (List.nodup_cons.mp (by simpa [Walk.vertices_cons] using hq)).1
    exact False.elim (hn (by simp [Walk.vertices]))

def Walk.reverse {v w : V} : Walk G v w → Walk G w v
  | .nil _ => .nil _
  | .cons h p => p.reverse.append (.cons (G.symm h) (.nil _))

theorem Walk.integral_reverse (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v)
    {v w : V} (p : Walk G v w) : p.reverse.integral r = p.integral r := by
  induction p with
  | nil => rfl
  | @cons v w z h p ih =>
    simp [Walk.reverse, Walk.integral_append, Walk.integral, ih, hr v w h, Bool.xor_comm]

theorem Walk.integral_path_independent (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v)
    (hc : CycleZero (G := G) r) {v w : V} (p q : Walk G v w) :
    p.integral r = q.integral r := by
  have hz := (p.append q.reverse).closed_zero_of_cycle_zero r hr hc
  rw [Walk.integral_append, Walk.integral_reverse r hr] at hz
  cases hp : p.integral r <;> cases hq : q.integral r <;> simp_all

def Reachable (G : SimpleGraph V) (v w : V) : Prop := Nonempty (Walk G v w)

-- Connectivity is witnessed by actual finite walks, including the empty walk.
def componentSetoid (G : SimpleGraph V) : Setoid V where
  r := Reachable G
  iseqv := {
    refl := fun v => ⟨.nil v⟩
    symm := fun ⟨p⟩ => ⟨p.reverse⟩
    trans := fun ⟨p⟩ ⟨q⟩ => ⟨p.append q⟩
  }

def Component (G : SimpleGraph V) := Quotient (componentSetoid G)

def component (G : SimpleGraph V) (v : V) : Component G := Quotient.mk _ v

noncomputable def representative (G : SimpleGraph V) (c : Component G) : V :=
  Classical.choose (Quotient.exists_rep c)

theorem component_representative (c : Component G) :
    component G (representative G c) = c := Classical.choose_spec (Quotient.exists_rep c)

noncomputable def root (G : SimpleGraph V) (v : V) : V :=
  representative G (component G v)

theorem root_reachable (v : V) : Reachable G (root G v) v := by
  exact Quotient.exact (component_representative (component G v))

theorem component_eq_of_reachable {v w : V} (h : Reachable G v w) :
    component G v = component G w := Quotient.sound h

theorem root_eq_of_reachable {v w : V} (h : Reachable G v w) :
    root G v = root G w := congrArg (representative G) (component_eq_of_reachable h)

theorem root_idempotent (v : V) : root G (root G v) = root G v :=
  root_eq_of_reachable (root_reachable v)

noncomputable def rootWalk (v : V) : Walk G (root G v) v :=
  Classical.choice (root_reachable v)

noncomputable def reconstruct (G : SimpleGraph V) (r : V → V → Bool) (v : V) : Bool :=
  (rootWalk (G := G) v).integral r

theorem edge_from_common_root (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v)
    (hc : CycleZero (G := G) r) {v w x y : V}
    (h : G.Adj v w) (p : Walk G x v) (q : Walk G y w) (hxy : x = y) :
    r v w = Bool.xor (p.integral r) (q.integral r) := by
  subst y
  have hi := (p.append (.cons h (.nil w))).integral_path_independent r hr hc q
  simp only [Walk.integral_append, Walk.integral, Bool.xor_false] at hi
  cases hp : p.integral r <;> cases hq : q.integral r <;> cases he : r v w <;> simp_all

theorem reconstruct_integrates (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v)
    (hc : CycleZero (G := G) r) : Integrates (G := G) r (reconstruct G r) := by
  intro v w h
  exact edge_from_common_root r hr hc h (rootWalk v) (rootWalk w)
    (root_eq_of_reachable ⟨.cons h (.nil w)⟩)

theorem integrable_iff_cycle_zero (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v) :
    (∃ a, Integrates (G := G) r a) ↔ CycleZero (G := G) r := by
  constructor
  · rintro ⟨a, ha⟩ v p _ _
    simpa using p.integral_of_integrates r a ha
  · intro hc
    exact ⟨reconstruct G r, reconstruct_integrates r hr hc⟩

theorem kernel_iff_componentwise_constant (a : V → Bool) :
    Integrates (G := G) (fun _ _ => false) a ↔
      ∀ v w, Reachable G v w → a v = a w := by
  constructor
  · intro ha v w ⟨p⟩
    have hz : p.integral (fun _ _ => false) = false := by
      clear ha
      induction p with
      | nil => rfl
      | cons h p ih => simpa [Walk.integral] using ih
    have hi : Bool.xor (a v) (a w) = false :=
      (p.integral_of_integrates (fun _ _ => false) a ha).symm.trans hz
    cases av : a v <;> cases aw : a w <;> simp_all
  · intro ha v w h
    have heq := ha v w ⟨.cons h (.nil w)⟩
    simp [heq]

theorem root_fixed_unique (r : V → V → Bool) (a b : V → Bool)
    (ha : Integrates (G := G) r a) (hb : Integrates (G := G) r b)
    (hroot : ∀ v, a (root G v) = b (root G v)) : a = b := by
  funext v
  have hi := (rootWalk v).integral_of_integrates r a ha
  have hj := (rootWalk v).integral_of_integrates r b hb
  rw [hi, hroot v] at hj
  cases av : a v <;> cases bv : b v <;> cases br : b (root G v) <;> simp_all

theorem Walk.integral_zero_of_same_end (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v)
    (hc : CycleZero (G := G) r) {v w : V} (p : Walk G v w) (h : v = w) :
    p.integral r = false := by
  subst w
  exact p.closed_zero_of_cycle_zero r hr hc

theorem reconstruct_at_root (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v)
    (hc : CycleZero (G := G) r) (v : V) : reconstruct G r (root G v) = false :=
  (rootWalk (root G v)).integral_zero_of_same_end r hr hc (root_idempotent v)

noncomputable def reconstructWith (G : SimpleGraph V) (r : V → V → Bool) (values : Component G → Bool)
    (v : V) : Bool := Bool.xor (values (component G v)) (reconstruct G r v)

theorem reconstruct_with_integrates (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v)
    (hc : CycleZero (G := G) r) (values : Component G → Bool) :
    Integrates (G := G) r (reconstructWith G r values) := by
  intro v w h
  have he := reconstruct_integrates r hr hc v w h
  have hcomp := component_eq_of_reachable (G := G) ⟨.cons h (.nil w)⟩
  simp only [reconstructWith, hcomp]
  rw [he]
  cases values (component G w) <;> cases reconstruct G r v <;> cases reconstruct G r w <;> decide

theorem reconstruct_with_at_root (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v)
    (hc : CycleZero (G := G) r) (values : Component G → Bool) (v : V) :
    reconstructWith G r values (root G v) = values (component G v) := by
  have hcomp := component_eq_of_reachable (root_reachable (G := G) v)
  simp [reconstructWith, reconstruct_at_root r hr hc, hcomp]

theorem reconstruction_classification (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v)
    (hc : CycleZero (G := G) r) (a : V → Bool) (ha : Integrates (G := G) r a) :
    ∃ values : Component G → Bool, reconstructWith G r values = a ∧
      ∀ other, reconstructWith G r other = a → other = values := by
  let values : Component G → Bool := fun c => a (representative G c)
  have heq : reconstructWith G r values = a := by
    apply root_fixed_unique r _ a (reconstruct_with_integrates r hr hc values) ha
    intro v
    exact reconstruct_with_at_root r hr hc values v
  refine ⟨values, heq, ?_⟩
  intro other hother
  funext c
  have h := congrFun hother (representative G c)
  have hroot : root G (representative G c) = representative G c := by
    change representative G (component G (representative G c)) = representative G c
    rw [component_representative c]
  have hcomp : component G (representative G c) = c := component_representative c
  have hv := reconstruct_with_at_root r hr hc other (representative G c)
  rw [hroot, hcomp] at hv
  exact hv.symm.trans h

end KRS.Graph
