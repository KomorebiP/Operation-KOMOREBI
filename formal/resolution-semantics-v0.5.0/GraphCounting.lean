import GraphSolver

/-!
Exact reconstruction counts for a graph with a certified finite component
index. Lists used for counting are proved complete and duplicate-free.
-/

namespace KRS.Graph

universe u v

theorem nodup_map_injective {A : Type u} {B : Type v} (f : A → B)
    (hf : Function.Injective f) (l : List A) (hl : l.Nodup) : (l.map f).Nodup := by
  exact List.Pairwise.map f (fun _ _ hne heq => hne (hf heq)) hl

theorem assignments_nodup (n : Nat) : (assignments n).Nodup := by
  induction n with
  | zero => simp [assignments]
  | succ n ih =>
    have hinj (b : Bool) : Function.Injective (extend (n := n) b) := by
      intro a d heq
      funext v
      exact congrFun heq v.succ
    apply List.nodup_append.mpr
    refine ⟨nodup_map_injective _ (hinj false) _ ih,
      nodup_map_injective _ (hinj true) _ ih, ?_⟩
    intro a ha b hb heq
    obtain ⟨x, _, rfl⟩ := List.mem_map.mp ha
    obtain ⟨y, _, rfl⟩ := List.mem_map.mp hb
    have bad := congrFun heq 0
    cases bad

theorem assignments_length (n : Nat) : (assignments n).length = 2 ^ n := by
  induction n with
  | zero => rfl
  | succ n ih => simp [assignments, ih, Nat.pow_succ, Nat.mul_two]

theorem count_of_nodup {A : Type u} [DecidableEq A] (l : List A) (hl : l.Nodup) (a : A) :
    l.count a = if a ∈ l then 1 else 0 := by
  induction l with
  | nil => simp
  | cons b l ih =>
    obtain ⟨hb, ht⟩ := List.nodup_cons.mp hl
    by_cases heq : b = a
    · subst b
      simp [List.count_eq_zero_of_not_mem hb]
    · simp [heq, Ne.symm heq, ih ht]

theorem same_members_length {A : Type u} (l s : List A) (hl : l.Nodup) (hs : s.Nodup)
    (hm : ∀ a, a ∈ l ↔ a ∈ s) : l.length = s.length := by
  classical
  apply List.Perm.length_eq
  apply List.perm_iff_count.mpr
  intro a
  rw [count_of_nodup l hl a, count_of_nodup s hs a]
  simp only [hm a]

structure ComponentIndex {V : Type u} (G : SimpleGraph V) (c : Nat) where
  label : V → Fin c
  vertex : Fin c → V
  edge_same : ∀ v w, G.Adj v w → label v = label w
  vertex_reachable : ∀ v, Reachable G (vertex (label v)) v
  label_vertex : ∀ i, label (vertex i) = i

def connectedComponentIndex {V : Type u} (G : SimpleGraph V) (rootVertex : V)
    (h : ∀ v, Reachable G rootVertex v) : ComponentIndex G 1 where
  label := fun _ => 0
  vertex := fun _ => rootVertex
  edge_same := fun _ _ _ => rfl
  vertex_reachable := h
  label_vertex := by intro i; apply Fin.ext; omega

variable {V : Type u} {G : SimpleGraph V} {c : Nat}

theorem ComponentIndex.label_reachable (I : ComponentIndex G c) {v w : V}
    (h : Reachable G v w) : I.label v = I.label w := by
  obtain ⟨p⟩ := h
  induction p with
  | nil => rfl
  | cons h p ih => exact (I.edge_same _ _ h).trans ih

def ComponentIndex.componentLabel (I : ComponentIndex G c) : Component G → Fin c :=
  Quotient.lift I.label (fun _ _ h => I.label_reachable h)

theorem ComponentIndex.component_label_vertex (I : ComponentIndex G c) (i : Fin c) :
    I.componentLabel (component G (I.vertex i)) = i := I.label_vertex i

theorem ComponentIndex.component_vertex_label (I : ComponentIndex G c) (q : Component G) :
    component G (I.vertex (I.componentLabel q)) = q := by
  refine Quotient.inductionOn q ?_
  intro v
  exact component_eq_of_reachable (I.vertex_reachable v)

noncomputable def indexedReconstruction (I : ComponentIndex G c) (r : V → V → Bool)
    (bits : Fin c → Bool) : V → Bool :=
  reconstructWith G r (fun q => bits (I.componentLabel q))

theorem indexed_reconstruction_injective (I : ComponentIndex G c) (r : V → V → Bool) :
    Function.Injective (indexedReconstruction I r) := by
  intro a b heq
  funext i
  have hv := congrFun heq (I.vertex i)
  change Bool.xor (a (I.label (I.vertex i))) (reconstruct G r (I.vertex i)) =
    Bool.xor (b (I.label (I.vertex i))) (reconstruct G r (I.vertex i)) at hv
  rw [I.label_vertex i] at hv
  cases ha : a i <;> cases hb : b i <;>
    cases hr : reconstruct G r (I.vertex i) <;> simp_all

theorem indexed_reconstruction_integrates (I : ComponentIndex G c) (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v) (hc : CycleZero (G := G) r)
    (bits : Fin c → Bool) : Integrates (G := G) r (indexedReconstruction I r bits) :=
  reconstruct_with_integrates r hr hc _

theorem indexed_reconstruction_surjective (I : ComponentIndex G c) (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v) (hc : CycleZero (G := G) r)
    (a : V → Bool) (ha : Integrates (G := G) r a) :
    ∃ bits : Fin c → Bool, indexedReconstruction I r bits = a := by
  obtain ⟨values, hvalues, _⟩ := reconstruction_classification r hr hc a ha
  let bits : Fin c → Bool := fun i => values (component G (I.vertex i))
  have hf : (fun q => bits (I.componentLabel q)) = values := by
    funext q
    exact congrArg values (I.component_vertex_label q)
  refine ⟨bits, ?_⟩
  simpa [indexedReconstruction, hf] using hvalues

noncomputable def reconstructionList (I : ComponentIndex G c) (r : V → V → Bool) :
    List (V → Bool) := (assignments c).map (indexedReconstruction I r)

theorem reconstruction_list_nodup (I : ComponentIndex G c) (r : V → V → Bool) :
    (reconstructionList I r).Nodup :=
  nodup_map_injective _ (indexed_reconstruction_injective I r) _ (assignments_nodup c)

theorem reconstruction_list_length (I : ComponentIndex G c) (r : V → V → Bool) :
    (reconstructionList I r).length = 2 ^ c := by
  simp [reconstructionList, assignments_length]

theorem reconstruction_list_complete (I : ComponentIndex G c) (r : V → V → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v) (hc : CycleZero (G := G) r)
    (a : V → Bool) : a ∈ reconstructionList I r ↔ Integrates (G := G) r a := by
  constructor
  · intro hm
    obtain ⟨bits, _, rfl⟩ := List.mem_map.mp hm
    exact indexed_reconstruction_integrates I r hr hc bits
  · intro ha
    obtain ⟨bits, heq⟩ := indexed_reconstruction_surjective I r hr hc a ha
    exact List.mem_map.mpr ⟨bits, assignments_complete c bits, heq⟩

def allSolutions {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) : List (Fin n → Bool) :=
  (assignments n).filter (checkSolution G r [])

theorem all_solutions_complete {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (a : Fin n → Bool) :
    a ∈ allSolutions G r ↔ Integrates (G := G) r a := by
  simp [allSolutions, List.mem_filter, assignments_complete, check_solution_true, PinsMatch]

theorem all_solutions_nodup {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) : (allSolutions G r).Nodup :=
  List.Pairwise.filter _ (assignments_nodup n)

theorem all_solutions_empty_iff {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) :
    allSolutions G r = [] ↔ ¬ ∃ a, Integrates (G := G) r a := by
  constructor
  · intro heq ⟨a, ha⟩
    have hm := (all_solutions_complete G r a).mpr ha
    simp [heq] at hm
  · intro hn
    cases hs : allSolutions G r with
    | nil => rfl
    | cons a tail =>
      have hm : a ∈ allSolutions G r := by simp [hs]
      exact False.elim (hn ⟨a, (all_solutions_complete G r a).mp hm⟩)

theorem all_solutions_count_of_cycle_zero {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (I : ComponentIndex G c) (r : Fin n → Fin n → Bool)
    (hr : ∀ v w, G.Adj v w → r v w = r w v) (hc : CycleZero (G := G) r) :
    (allSolutions G r).length = 2 ^ c := by
  rw [← reconstruction_list_length I r]
  apply same_members_length _ _ (all_solutions_nodup G r) (reconstruction_list_nodup I r)
  intro a
  rw [all_solutions_complete, reconstruction_list_complete I r hr hc]

theorem integrating_field_symmetric (r : V → V → Bool) (a : V → Bool)
    (ha : Integrates (G := G) r a) : ∀ v w, G.Adj v w → r v w = r w v := by
  intro v w h
  rw [ha v w h, ha w v (G.symm h), Bool.xor_comm]

theorem all_solutions_count {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (I : ComponentIndex G c) (r : Fin n → Fin n → Bool)
    (ha : ∃ a, Integrates (G := G) r a) : (allSolutions G r).length = 2 ^ c := by
  obtain ⟨a, ha⟩ := ha
  have hr := integrating_field_symmetric r a ha
  exact all_solutions_count_of_cycle_zero G I r hr ((integrable_iff_cycle_zero r hr).mp ⟨a, ha⟩)

def distinctValues {A : Type u} [DecidableEq A] : List A → List A
  | [] => []
  | a :: tail =>
    let values := distinctValues tail
    if a ∈ values then values else a :: values

theorem distinct_values_complete {A : Type u} [DecidableEq A] (l : List A) (a : A) :
    a ∈ distinctValues l ↔ a ∈ l := by
  induction l with
  | nil => simp [distinctValues]
  | cons b tail ih =>
    by_cases hb : b ∈ distinctValues tail
    · simp only [distinctValues, if_pos hb]
      constructor
      · intro ha
        exact List.mem_cons_of_mem b (ih.mp ha)
      · intro ha
        rcases List.mem_cons.mp ha with heq | hm
        · subst a
          exact hb
        · exact ih.mpr hm
    · simp [distinctValues, hb, ih]

theorem distinct_values_nodup {A : Type u} [DecidableEq A] (l : List A) :
    (distinctValues l).Nodup := by
  induction l with
  | nil => simp [distinctValues]
  | cons a tail ih =>
    by_cases ha : a ∈ distinctValues tail
    · simpa [distinctValues, ha] using ih
    · simpa [distinctValues, ha] using List.nodup_cons.mpr ⟨ha, ih⟩

theorem nodup_get_injective {A : Type u} (l : List A) (hl : l.Nodup) :
    Function.Injective l.get := by
  induction l with
  | nil => intro i; exact Fin.elim0 i
  | cons a tail ih =>
    obtain ⟨ha, ht⟩ := List.nodup_cons.mp hl
    intro i
    refine Fin.cases ?_ (fun i => ?_) i
    · intro j
      refine Fin.cases ?_ (fun j => ?_) j
      · intro _
        rfl
      · intro heq
        change a = tail.get j at heq
        have hm := tail.get_mem j
        rw [← heq] at hm
        exact False.elim (ha hm)
    · intro j
      refine Fin.cases ?_ (fun j => ?_) j
      · intro heq
        change tail.get i = a at heq
        have hm := tail.get_mem i
        rw [heq] at hm
        exact False.elim (ha hm)
      · intro heq
        change tail.get i = tail.get j at heq
        exact congrArg Fin.succ (ih ht heq)

noncomputable def componentList {n : Nat} (G : SimpleGraph (Fin n)) : List (Component G) := by
  classical
  exact distinctValues (List.ofFn (component G))

theorem component_list_nodup {n : Nat} (G : SimpleGraph (Fin n)) : (componentList G).Nodup := by
  classical
  exact distinct_values_nodup _

theorem component_list_complete {n : Nat} (G : SimpleGraph (Fin n)) (q : Component G) :
    q ∈ componentList G := by
  classical
  obtain ⟨v, hv⟩ := Quotient.exists_rep q
  apply (distinct_values_complete _ q).mpr
  exact List.mem_ofFn.mpr ⟨v, hv⟩

noncomputable def componentPosition {n : Nat} (G : SimpleGraph (Fin n)) (q : Component G) :
    Fin (componentList G).length :=
  Classical.choose (List.mem_iff_get.mp (component_list_complete G q))

theorem component_get_position {n : Nat} (G : SimpleGraph (Fin n)) (q : Component G) :
    (componentList G).get (componentPosition G q) = q :=
  Classical.choose_spec (List.mem_iff_get.mp (component_list_complete G q))

theorem component_position_get {n : Nat} (G : SimpleGraph (Fin n))
    (i : Fin (componentList G).length) :
    componentPosition G ((componentList G).get i) = i :=
  nodup_get_injective _ (component_list_nodup G) (component_get_position G _)

noncomputable def componentCount {n : Nat} (G : SimpleGraph (Fin n)) : Nat := (componentList G).length

noncomputable def canonicalComponentIndex {n : Nat} (G : SimpleGraph (Fin n)) :
    ComponentIndex G (componentCount G) where
  label := fun v => componentPosition G (component G v)
  vertex := fun i => representative G ((componentList G).get i)
  edge_same := fun v w h => congrArg (componentPosition G)
    (component_eq_of_reachable ⟨.cons h (.nil w)⟩)
  vertex_reachable := by
    intro v
    change Reachable G (representative G ((componentList G).get (componentPosition G (component G v)))) v
    rw [component_get_position]
    exact root_reachable v
  label_vertex := by
    intro i
    change componentPosition G (component G (representative G ((componentList G).get i))) = i
    rw [component_representative]
    exact component_position_get G i

theorem all_solutions_count_by_components {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (ha : ∃ a, Integrates (G := G) r a) :
    (allSolutions G r).length = 2 ^ componentCount G :=
  all_solutions_count G (canonicalComponentIndex G) r ha

end KRS.Graph
