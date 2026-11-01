import GraphCounting

/-!
Exact counts for arbitrary lists of vertex pins. Counts are conditional on
joint satisfiability of the edge equations and pins; inconsistent data have
no solutions. Components, rather than entries in the pin list, remove choices.
-/

namespace KRS.Graph

def MaskMatch {n : Nat} (bits mask : Fin n → Bool) : Prop :=
  ∀ i, mask i = true → bits i = false

def freeCount : (n : Nat) → (Fin n → Bool) → Nat
  | 0, _ => 0
  | n + 1, mask => freeCount n (fun i => mask i.succ) + if mask 0 then 0 else 1

def freeAssignments : (n : Nat) → (Fin n → Bool) → List (Fin n → Bool)
  | 0, _ => [fun v => Fin.elim0 v]
  | n + 1, mask =>
      let tail := freeAssignments n (fun i => mask i.succ)
      if mask 0 then tail.map (extend false)
      else tail.map (extend false) ++ tail.map (extend true)

theorem mem_map_extend {n : Nat} (b : Bool) (l : List (Fin n → Bool))
    (a : Fin (n + 1) → Bool) :
    a ∈ l.map (extend b) ↔ a 0 = b ∧ (fun i => a i.succ) ∈ l := by
  constructor
  · intro hm
    obtain ⟨tail, ht, heq⟩ := List.mem_map.mp hm
    refine ⟨(congrFun heq 0).symm, ?_⟩
    have htail : (fun i => a i.succ) = tail := by
      funext i
      exact (congrFun heq i.succ).symm
    simpa [htail] using ht
  · rintro ⟨hb, ht⟩
    apply List.mem_map.mpr
    refine ⟨fun i => a i.succ, ht, ?_⟩
    funext v
    exact Fin.cases hb.symm (fun _ => rfl) v

theorem mask_match_succ {n : Nat} (a mask : Fin (n + 1) → Bool) :
    MaskMatch a mask ↔ (mask 0 = true → a 0 = false) ∧
      MaskMatch (fun i => a i.succ) (fun i => mask i.succ) := by
  constructor
  · intro h
    exact ⟨h 0, fun i => h i.succ⟩
  · rintro ⟨h0, ht⟩ v
    exact Fin.cases h0 ht v

theorem free_assignments_complete (n : Nat) (mask bits : Fin n → Bool) :
    bits ∈ freeAssignments n mask ↔ MaskMatch bits mask := by
  induction n with
  | zero =>
    have heq : bits = (fun v : Fin 0 => Fin.elim0 v) := by funext v; exact Fin.elim0 v
    constructor
    · intro _ v
      exact Fin.elim0 v
    · intro _
      simp [freeAssignments, heq]
  | succ n ih =>
    rw [mask_match_succ]
    cases hm : mask 0 <;> cases hb : bits 0 <;>
      simp [freeAssignments, hm, List.mem_append, mem_map_extend, ih, hb]

theorem free_assignments_nodup (n : Nat) (mask : Fin n → Bool) :
    (freeAssignments n mask).Nodup := by
  induction n with
  | zero => simp [freeAssignments]
  | succ n ih =>
    have hinj (b : Bool) : Function.Injective (extend (n := n) b) := by
      intro a d heq
      funext v
      exact congrFun heq v.succ
    cases hm : mask 0
    · simp only [freeAssignments, hm, Bool.false_eq_true, ↓reduceIte]
      apply List.nodup_append.mpr
      refine ⟨nodup_map_injective _ (hinj false) _ (ih _),
        nodup_map_injective _ (hinj true) _ (ih _), ?_⟩
      intro a ha b hb heq
      obtain ⟨x, _, rfl⟩ := List.mem_map.mp ha
      obtain ⟨y, _, rfl⟩ := List.mem_map.mp hb
      have bad := congrFun heq 0
      cases bad
    · simpa [freeAssignments, hm] using
        nodup_map_injective _ (hinj false) _ (ih (fun i => mask i.succ))

theorem free_assignments_length (n : Nat) (mask : Fin n → Bool) :
    (freeAssignments n mask).length = 2 ^ freeCount n mask := by
  induction n with
  | zero => rfl
  | succ n ih =>
    cases hm : mask 0 <;>
      simp [freeAssignments, freeCount, hm, ih, Nat.pow_succ, Nat.mul_two]

theorem free_count_eq_filter_get {A : Type} (l : List A) (mask : A → Bool) :
    freeCount l.length (fun i => mask (l.get i)) = (l.filter (fun a => !mask a)).length := by
  induction l with
  | nil => rfl
  | cons a tail ih =>
    cases hm : mask a <;> simp [freeCount, hm, Nat.add_comm] <;> exact ih

def pinnedMask {n c : Nat} {G : SimpleGraph (Fin n)} (I : ComponentIndex G c)
    (pins : List (Fin n × Bool)) (i : Fin c) : Bool :=
  pins.any (fun pin => I.label pin.1 == i)

theorem pinned_mask_true_iff {n c : Nat} {G : SimpleGraph (Fin n)}
    (I : ComponentIndex G c) (pins : List (Fin n × Bool)) (i : Fin c) :
    pinnedMask I pins i = true ↔ ∃ v b, (v, b) ∈ pins ∧ I.label v = i := by
  simp only [pinnedMask, List.any_eq_true, beq_iff_eq]
  constructor
  · rintro ⟨⟨v, b⟩, hm, heq⟩
    exact ⟨v, b, hm, heq⟩
  · rintro ⟨v, b, hm, heq⟩
    exact ⟨(v, b), hm, heq⟩

def shiftBy {n c : Nat} {G : SimpleGraph (Fin n)} (I : ComponentIndex G c)
    (base : Fin n → Bool) (bits : Fin c → Bool) (v : Fin n) : Bool :=
  Bool.xor (bits (I.label v)) (base v)

theorem shift_by_injective {n c : Nat} {G : SimpleGraph (Fin n)}
    (I : ComponentIndex G c) (base : Fin n → Bool) : Function.Injective (shiftBy I base) := by
  intro a b heq
  funext i
  have hv := congrFun heq (I.vertex i)
  simp only [shiftBy, I.label_vertex] at hv
  cases ha : a i <;> cases hb : b i <;> cases hvb : base (I.vertex i) <;> simp_all

theorem shift_by_integrates {n c : Nat} {G : SimpleGraph (Fin n)}
    (I : ComponentIndex G c) (r : Fin n → Fin n → Bool) (base : Fin n → Bool)
    (ha : Integrates (G := G) r base) (bits : Fin c → Bool) :
    Integrates (G := G) r (shiftBy I base bits) := by
  intro v w h
  rw [ha v w h]
  simp only [shiftBy, I.edge_same v w h]
  cases bits (I.label w) <;> cases base v <;> cases base w <;> decide

theorem integrating_difference_constant {n : Nat} {G : SimpleGraph (Fin n)}
    (r : Fin n → Fin n → Bool) (a b : Fin n → Bool)
    (ha : Integrates (G := G) r a) (hb : Integrates (G := G) r b)
    (v w : Fin n) (h : Reachable G v w) :
    Bool.xor (a v) (b v) = Bool.xor (a w) (b w) := by
  obtain ⟨p⟩ := h
  have hi := (p.integral_of_integrates r a ha).symm.trans (p.integral_of_integrates r b hb)
  cases av : a v <;> cases aw : a w <;> cases bv : b v <;> cases bw : b w <;> simp_all

theorem shift_by_surjective {n c : Nat} {G : SimpleGraph (Fin n)}
    (I : ComponentIndex G c) (r : Fin n → Fin n → Bool) (base a : Fin n → Bool)
    (hb : Integrates (G := G) r base) (ha : Integrates (G := G) r a) :
    ∃ bits, shiftBy I base bits = a := by
  refine ⟨fun i => Bool.xor (a (I.vertex i)) (base (I.vertex i)), ?_⟩
  funext v
  have hd := integrating_difference_constant r a base ha hb _ v (I.vertex_reachable v)
  change Bool.xor (Bool.xor (a (I.vertex (I.label v))) (base (I.vertex (I.label v)))) (base v) = a v
  rw [hd]
  cases a v <;> cases base v <;> decide

theorem pins_match_iff_pointwise {n : Nat} (a : Fin n → Bool) (pins : List (Fin n × Bool)) :
    PinsMatch a pins ↔ ∀ v b, (v, b) ∈ pins → a v = b := by
  constructor
  · exact fun h v b hm => pins_match_at_vertex a pins h v b hm
  · intro h
    apply List.all_eq_true.mpr
    rintro ⟨v, b⟩ hm
    exact beq_iff_eq.mpr (h v b hm)

theorem shift_by_pins_iff {n c : Nat} {G : SimpleGraph (Fin n)}
    (I : ComponentIndex G c) (base : Fin n → Bool) (pins : List (Fin n × Bool))
    (hp : PinsMatch base pins) (bits : Fin c → Bool) :
    PinsMatch (shiftBy I base bits) pins ↔ MaskMatch bits (pinnedMask I pins) := by
  constructor
  · intro h i hi
    obtain ⟨v, b, hm, hv⟩ := (pinned_mask_true_iff I pins i).mp hi
    have h1 := pins_match_at_vertex _ pins h v b hm
    have h2 := pins_match_at_vertex base pins hp v b hm
    simp only [shiftBy, hv, h2] at h1
    cases hb : b <;> cases hi : bits i <;> simp_all
  · intro h
    apply (pins_match_iff_pointwise _ pins).mpr
    intro v b hm
    have hi := h (I.label v) ((pinned_mask_true_iff I pins _).mpr ⟨v, b, hm, rfl⟩)
    simpa [shiftBy, hi] using pins_match_at_vertex base pins hp v b hm

def pinnedSolutions {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) : List (Fin n → Bool) :=
  (assignments n).filter (checkSolution G r pins)

theorem pinned_solutions_complete {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) (a : Fin n → Bool) :
    a ∈ pinnedSolutions G r pins ↔ Integrates (G := G) r a ∧ PinsMatch a pins := by
  simp [pinnedSolutions, List.mem_filter, assignments_complete, check_solution_true]

theorem pinned_solutions_nodup {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) :
    (pinnedSolutions G r pins).Nodup :=
  List.Pairwise.filter _ (assignments_nodup n)

theorem pinned_solutions_empty_iff {n : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) :
    pinnedSolutions G r pins = [] ↔ ¬ ∃ a, Integrates (G := G) r a ∧ PinsMatch a pins := by
  constructor
  · intro h ⟨a, ha⟩
    have hm := (pinned_solutions_complete G r pins a).mpr ha
    simp [h] at hm
  · intro h
    cases hs : pinnedSolutions G r pins with
    | nil => rfl
    | cons a tail =>
      exact False.elim (h ⟨a, (pinned_solutions_complete G r pins a).mp (by simp [hs])⟩)

theorem pinned_solutions_count {n c : Nat} (G : SimpleGraph (Fin n)) [DecidableRel G.Adj]
    (I : ComponentIndex G c) (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool))
    (ha : ∃ a, Integrates (G := G) r a ∧ PinsMatch a pins) :
    (pinnedSolutions G r pins).length = 2 ^ freeCount c (pinnedMask I pins) := by
  obtain ⟨base, hb, hp⟩ := ha
  let choices := freeAssignments c (pinnedMask I pins)
  let reconstructions := choices.map (shiftBy I base)
  have hn : reconstructions.Nodup :=
    nodup_map_injective _ (shift_by_injective I base) _ (free_assignments_nodup c _)
  have heq : (pinnedSolutions G r pins).length = reconstructions.length := by
    apply same_members_length _ _ (pinned_solutions_nodup G r pins) hn
    intro a
    rw [pinned_solutions_complete]
    constructor
    · rintro ⟨hai, hpa⟩
      obtain ⟨bits, hbits⟩ := shift_by_surjective I r base a hb hai
      apply List.mem_map.mpr
      refine ⟨bits, ?_, hbits⟩
      apply (free_assignments_complete c _ bits).mpr
      apply (shift_by_pins_iff I base pins hp bits).mp
      simpa [hbits] using hpa
    · intro hm
      change a ∈ choices.map (shiftBy I base) at hm
      obtain ⟨bits, hchoice, rfl⟩ := List.mem_map.mp hm
      exact ⟨shift_by_integrates I r base hb bits,
        (shift_by_pins_iff I base pins hp bits).mpr ((free_assignments_complete c _ bits).mp hchoice)⟩
  rw [heq]
  simpa [reconstructions, choices] using free_assignments_length c (pinnedMask I pins)

theorem component_position_injective {n : Nat} (G : SimpleGraph (Fin n)) :
    Function.Injective (componentPosition G) := by
  intro q s heq
  have h := congrArg (componentList G).get heq
  simpa only [component_get_position] using h

theorem canonical_pinned_mask_true_iff {n : Nat} (G : SimpleGraph (Fin n))
    (pins : List (Fin n × Bool)) (q : Component G) :
    pinnedMask (canonicalComponentIndex G) pins (componentPosition G q) = true ↔
      ∃ v b, (v, b) ∈ pins ∧ component G v = q := by
  rw [pinned_mask_true_iff]
  constructor
  · rintro ⟨v, b, hm, heq⟩
    exact ⟨v, b, hm, component_position_injective G heq⟩
  · rintro ⟨v, b, hm, heq⟩
    exact ⟨v, b, hm, congrArg (componentPosition G) heq⟩

noncomputable def unpinnedComponents {n : Nat} (G : SimpleGraph (Fin n))
    (pins : List (Fin n × Bool)) : List (Component G) :=
  (componentList G).filter (fun q => !pinnedMask (canonicalComponentIndex G) pins (componentPosition G q))

theorem unpinned_components_complete {n : Nat} (G : SimpleGraph (Fin n))
    (pins : List (Fin n × Bool)) (q : Component G) :
    q ∈ unpinnedComponents G pins ↔
      ∀ v b, (v, b) ∈ pins → component G v ≠ q := by
  constructor
  · intro hm v b hp heq
    have hmask := (List.mem_filter.mp hm).2
    have htrue := (canonical_pinned_mask_true_iff G pins q).mpr ⟨v, b, hp, heq⟩
    simp [htrue] at hmask
  · intro h
    apply List.mem_filter.mpr
    refine ⟨component_list_complete G q, ?_⟩
    cases hm : pinnedMask (canonicalComponentIndex G) pins (componentPosition G q) with
    | false => rfl
    | true =>
      obtain ⟨v, b, hp, heq⟩ := (canonical_pinned_mask_true_iff G pins q).mp hm
      exact False.elim (h v b hp heq)

theorem unpinned_components_nodup {n : Nat} (G : SimpleGraph (Fin n))
    (pins : List (Fin n × Bool)) : (unpinnedComponents G pins).Nodup :=
  List.Pairwise.filter _ (component_list_nodup G)

noncomputable def unpinnedComponentCount {n : Nat} (G : SimpleGraph (Fin n))
    (pins : List (Fin n × Bool)) : Nat := (unpinnedComponents G pins).length

theorem unpinned_component_count_eq_free_count {n : Nat} (G : SimpleGraph (Fin n))
    (pins : List (Fin n × Bool)) : unpinnedComponentCount G pins =
      freeCount (componentCount G) (pinnedMask (canonicalComponentIndex G) pins) := by
  unfold unpinnedComponentCount unpinnedComponents
  rw [← free_count_eq_filter_get]
  congr 1
  funext i
  rw [component_position_get]

theorem pinned_solutions_count_by_components {n : Nat} (G : SimpleGraph (Fin n))
    [DecidableRel G.Adj] (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool))
    (ha : ∃ a, Integrates (G := G) r a ∧ PinsMatch a pins) :
    (pinnedSolutions G r pins).length = 2 ^ unpinnedComponentCount G pins := by
  rw [unpinned_component_count_eq_free_count]
  exact pinned_solutions_count G (canonicalComponentIndex G) r pins ha

theorem pinned_solutions_count_total {n : Nat} (G : SimpleGraph (Fin n))
    [DecidableRel G.Adj] (r : Fin n → Fin n → Bool) (pins : List (Fin n × Bool)) :
    (pinnedSolutions G r pins).length =
      if (solve G r pins).isSome then 2 ^ unpinnedComponentCount G pins else 0 := by
  cases hs : solve G r pins with
  | none =>
    have hn := (solve_none_iff_no_solution G r pins).mp hs
    rw [(pinned_solutions_empty_iff G r pins).mpr hn]
    rfl
  | some a =>
    exact pinned_solutions_count_by_components G r pins ⟨a, solve_sound G r pins a hs⟩

theorem pinned_solutions_no_pins {n : Nat} (G : SimpleGraph (Fin n))
    [DecidableRel G.Adj] (r : Fin n → Fin n → Bool) :
    pinnedSolutions G r [] = allSolutions G r := rfl

theorem unpinned_component_count_no_pins {n : Nat} (G : SimpleGraph (Fin n)) :
    unpinnedComponentCount G [] = componentCount G := by
  simp [unpinnedComponentCount, unpinnedComponents, pinnedMask, componentCount]

end KRS.Graph
