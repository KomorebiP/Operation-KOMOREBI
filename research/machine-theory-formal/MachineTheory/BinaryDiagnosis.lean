import MachineTheory.BinaryStructure

/-!
# Core 5.3: lower bounds for the actual inquiry model

Immutability and singleton success are premises of identification, not consequences
of binary reports. Terminal work is charged. Total availability is not needed for
the lower bound, so the source's total-query case is included as a specialization.
-/
namespace Komorebi.MachineTheory.BinaryDiagnosis
open HardInquiry Finset
variable {X E C : Type} [DecidableEq X]

/-- The exact scope in which counting hidden cases counts required repair leaves. -/
structure Scope (M : Model X E Bool C Unit) : Prop where
  immutable : ∀ e x, M.next e x = x
  singleton : ∀ c x y, M.accept x c = true → M.accept y c = true → x = y
  query_cost : ∀ e, M.stepCost e () = 1
  terminal_cost : ∀ c V, V.Nonempty → M.terminalCost c V () = 1

/-- Validity rules out internal nodes with no possible successor. -/
theorem valid_live (M : Model X E Bool C Unit) (h : ℕ) (V : Finset X)
    (t : Tree E Bool C h) (ht : M.Valid h V t) : Live h t := by
  induction h generalizing V with
  | zero => trivial
  | succ h ih =>
    cases t with
    | inl c => trivial
    | inr ek =>
      obtain ⟨e,k⟩ := ek
      constructor
      · obtain ⟨x,hx⟩ := ht.1.1
        obtain ⟨u,hu,_⟩ := (M.valid_child ht (M.observe e x)).mp ⟨_,M.actual_next_mem hx e⟩
        cases ho : M.observe e x with
        | false =>
          rw [ho] at hu
          exact Or.inl (by simp only [hu,ne_eq,reduceCtorEq,not_false_eq_true])
        | true =>
          rw [ho] at hu
          exact Or.inr (by simp only [hu,ne_eq,reduceCtorEq,not_false_eq_true])
      · intro o u hu
        exact ih (M.update V e o) u (by simpa only [hu] using ht.2 o)

theorem update_immutable (M : Model X E Bool C Unit) (s : Scope M)
    (V : Finset X) (e : E) (o : Bool) :
    M.update V e o = V.filter (fun x => M.observe e x = o) := by
  have he : M.next e = id := funext (s.immutable e)
  simp only [Model.update,he,Finset.image_id]

/-- The two reachable supports partition, rather than duplicate, the initial cases. -/
theorem binary_card_split (M : Model X E Bool C Unit) (s : Scope M)
    (V : Finset X) (e : E) :
    V.card = (M.update V e false).card + (M.update V e true).card := by
  rw [update_immutable M s,update_immutable M s]
  have he : V.filter (fun x => M.observe e x = true) = V.filter (fun x => ¬ M.observe e x = false) := by
    ext x
    cases M.observe e x <;> simp
  rw [he]
  exact (Finset.card_filter_add_card_filter_not (s := V) (fun x => M.observe e x = false)).symm

omit [DecidableEq X] in
/-- No two distinct immutable cases can share an acceptable repair leaf. -/
theorem terminal_card_one (M : Model X E Bool C Unit) (s : Scope M)
    (V : Finset X) (c : C) (ht : M.Terminal V c) : V.card = 1 := by
  obtain ⟨x,hx⟩ := ht.1
  have he : V = {x} := by
    ext y
    simp only [mem_singleton]
    constructor
    · intro hy
      exact s.singleton c y x (ht.2 y hy) (ht.2 x hx)
    · intro hy
      simpa only [hy] using hx
  simp only [he,card_singleton]

/-- Recursive distinct-leaf accounting is derived from the actual success predicate. -/
theorem cases_le_leaves (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h) (ht : M.Valid h V t) :
    V.card ≤ leaves h t := by
  induction h generalizing V with
  | zero => exact (terminal_card_one M s V t ht).le
  | succ h ih =>
    cases t with
    | inl c => exact (terminal_card_one M s V c ht).le
    | inr ek =>
      obtain ⟨e,k⟩ := ek
      have branch : ∀ o, (M.update V e o).card ≤ ((k o).map (leaves h)).getD 0 := by
        intro o
        cases ho : k o with
        | none =>
          have he : M.update V e o = ∅ := by simpa only [ho] using ht.2 o
          simp only [he,card_empty,Option.map_none,Option.getD_none,le_refl]
        | some u =>
          exact ih (M.update V e o) u (by simpa only [ho] using ht.2 o)
      rw [binary_card_split M s V e]
      exact Nat.add_le_add (branch false) (branch true)

/-- In this exact deterministic scope, every retained leaf has precisely one case. -/
theorem cases_eq_leaves (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h) (ht : M.Valid h V t) :
    V.card = leaves h t := by
  induction h generalizing V with
  | zero => exact terminal_card_one M s V t ht
  | succ h ih =>
    cases t with
    | inl c => exact terminal_card_one M s V c ht
    | inr ek =>
      obtain ⟨e,k⟩ := ek
      have branch : ∀ o, (M.update V e o).card = ((k o).map (leaves h)).getD 0 := by
        intro o
        cases ho : k o with
        | none =>
          have he : M.update V e o = ∅ := by simpa only [ho] using ht.2 o
          simp only [he,card_empty,Option.map_none,Option.getD_none]
        | some u => exact ih _ u (by simpa only [ho] using ht.2 o)
      rw [binary_card_split M s V e,branch false,branch true]
      rfl

/-- Every redundant unary query increases installed storage by exactly one record. -/
theorem records_exact (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h) (ht : M.Valid h V t) :
    (M.profile h V t).2 = 2 * V.card - 1 + unary h t := by
  have hc := cases_eq_leaves M s h V t ht
  have hr := records_identity h t (valid_live M h V t ht)
  have hn : 0 < V.card := Finset.card_pos.mpr (M.valid_nonempty ht)
  rw [M.profile_records]
  omega

/-- Minimum literal storage excludes all unary nodes in this scope. -/
theorem minimum_records_iff_no_unary (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h) (ht : M.Valid h V t) :
    (M.profile h V t).2 = 2 * V.card - 1 ↔ unary h t = 0 := by
  rw [records_exact M s h V t ht]
  omega

/-- Under unit costs, the full worst-case work is actual query depth plus repair. -/
theorem work_eq_depth_succ (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h) (ht : M.Valid h V t) :
    (M.profile h V t).1 () = 1 + depth h t := by
  induction h generalizing V with
  | zero => exact s.terminal_cost t V ht.1
  | succ h ih =>
    cases t with
    | inl c => exact s.terminal_cost c V ht.1
    | inr ek =>
      obtain ⟨e,k⟩ := ek
      have hf := ht.2 false
      have hg := ht.2 true
      have live := (valid_live M (h+1) V (.inr (e,k)) ht).1
      change M.stepCost e () + _ = 1 + depth (h+1) (.inr (e,k))
      rw [s.query_cost e]
      cases he : k false with
      | none =>
        cases hgk : k true with
        | none => simp only [he,hgk,ne_eq,not_true_eq_false,or_self] at live
        | some r =>
          have hr := ih _ r (by simpa only [hgk] using hg)
          simp [depth,he,hgk,Model.optional,Fintype.univ_bool,hr]
      | some l =>
        have hl := ih _ l (by simpa only [he] using hf)
        cases hgk : k true with
        | none =>
          simp [depth,he,hgk,Model.optional,Fintype.univ_bool,hl]
        | some r =>
          have hr := ih _ r (by simpa only [hgk] using hg)
          simp only [depth,he,hgk,Option.map_some,Option.getD_some,Model.optional,
            Fintype.univ_bool,Finset.sup_insert,Finset.sup_singleton,hr,hl]
          omega

/-- General lower bounds, including actual depth and literal unary records. -/
theorem binary_lower_bounds (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h) (ht : M.Valid h V t) :
    Nat.clog 2 V.card ≤ depth h t ∧
    1 + Nat.clog 2 V.card ≤ (M.profile h V t).1 () ∧
    2 * V.card - 1 ≤ (M.profile h V t).2 := by
  have hc := cases_le_leaves M s h V t ht
  have hd := Nat.clog_le_of_le_pow (hc.trans (leaves_le_pow_depth h t))
  refine ⟨hd,?_,?_⟩
  · rw [work_eq_depth_succ M s h V t ht]
    exact Nat.add_le_add_left hd 1
  · rw [M.profile_records]
    have hr := records_lower h t (valid_live M h V t ht)
    omega

/-- No controller can compensate for an insufficient experiment horizon. -/
theorem impossible_below_information_depth (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (hh : h < Nat.clog 2 V.card) :
    ¬ ∃ t : Tree E Bool C h, M.Valid h V t := by
  rintro ⟨t,ht⟩
  exact (not_le_of_gt hh) ((binary_lower_bounds M s h V t ht).1.trans (depth_le_horizon h t))

/-- Coordinatewise unavoidable work and storage; no assumption that they are attainable. -/
def lowerProfile (n : ℕ) : Profile Unit := (fun _ => 1 + Nat.clog 2 n, 2*n-1)

theorem lowerProfile_le (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h) (ht : M.Valid h V t) :
    lowerProfile V.card ≤ M.profile h V t := by
  have hb := binary_lower_bounds M s h V t ht
  refine ⟨?_,hb.2.2⟩
  intro r
  cases r
  exact hb.2.1

variable [Fintype E] [Fintype C]

/-- Core 5.3: a VALID candidate meeting BOTH bounds closes the exact Pareto search. -/
theorem checked_candidate_closes_frontier (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h) (ht : M.Valid h V t)
    (hw : (M.profile h V t).1 () = 1 + Nat.clog 2 V.card)
    (hm : (M.profile h V t).2 = 2 * V.card - 1) :
    M.solve h V = {lowerProfile V.card} := by
  classical
  have he : M.profile h V t = lowerProfile V.card := by
    apply Prod.ext
    · funext r; cases r; exact hw
    · exact hm
  have hs : lowerProfile V.card ∈ M.solve h V := by
    apply (M.exact_frontier h V _).mpr
    exact ⟨⟨t,ht,he⟩,fun u hu _ => lowerProfile_le M s h V u hu⟩
  ext p
  simp only [mem_singleton]
  constructor
  · intro hp
    obtain ⟨u,hu,hup⟩ := M.solve_witness h V p hp
    have hl : lowerProfile V.card ≤ p := hup ▸ lowerProfile_le M s h V u hu
    exact le_antisymm (M.solve_antichain h V hp hs hl) hl
  · rintro rfl; exact hs

/-- Early return agrees with the actual executable profile recurrence. -/
theorem checked_candidate_closes_compute (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h) (ht : M.Valid h V t)
    (hw : (M.profile h V t).1 () = 1 + Nat.clog 2 V.card)
    (hm : (M.profile h V t).2 = 2 * V.card - 1) :
    M.compute h V = {lowerProfile V.card} := by
  rw [M.compute_eq_solve]
  exact checked_candidate_closes_frontier M s h V t ht hw hm

/-- A data-only certificate gate; a false result means no certificate, not infeasibility. -/
def checkCandidate (M : Model X E Bool C Unit) (h : ℕ) (V : Finset X)
    (t : Tree E Bool C h) : Bool :=
  decide (M.Valid h V t ∧ M.profile h V t = lowerProfile V.card)

omit [Fintype E] [Fintype C] in
theorem checkCandidate_iff (M : Model X E Bool C Unit) (h : ℕ) (V : Finset X)
    (t : Tree E Bool C h) : checkCandidate M h V t = true ↔
      M.Valid h V t ∧ M.profile h V t = lowerProfile V.card := by
  simp only [checkCandidate,decide_eq_true_eq]

/-- The executable certificate does not run the exhaustive profile synthesizer. -/
theorem checked_early_return (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h)
    (hc : checkCandidate M h V t = true) : M.compute h V = {lowerProfile V.card} := by
  obtain ⟨hv,hp⟩ := (checkCandidate_iff M h V t).mp hc
  apply checked_candidate_closes_compute M s h V t hv
  · exact congrArg (fun p : Profile Unit => p.1 ()) hp
  · exact congrArg Prod.snd hp

/-- Any larger allowed horizon has the same frontier once both bounds are attained. -/
theorem closed_frontier_all_larger_horizons (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h)
    (hc : checkCandidate M h V t = true) (n : ℕ) :
    M.solve (h+n) V = {lowerProfile V.card} := by
  obtain ⟨hv,hp⟩ := (checkCandidate_iff M h V t).mp hc
  obtain ⟨u,hu,hup⟩ := M.pad_horizon h n V t hv
  have he := hup.trans hp
  exact checked_candidate_closes_frontier M s (h+n) V u hu
    (congrArg (fun p : Profile Unit => p.1 ()) he) (congrArg Prod.snd he)

end Komorebi.MachineTheory.BinaryDiagnosis
