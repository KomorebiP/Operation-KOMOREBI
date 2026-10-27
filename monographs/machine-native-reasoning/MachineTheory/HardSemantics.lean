import MachineTheory.HardExecution

/-! # Horizon embeddings, closed resource invariants and attained worst-case work -/
namespace Komorebi.MachineTheory.HardInquiry
open Finset
variable {X E O C R : Type}
namespace Model

/-- Increase the permitted horizon without inserting an experiment. -/
def promote : (h : ℕ) → Tree E O C h → Tree E O C (h+1)
  | 0, c => .inl c
  | _+1, .inl c => .inl c
  | h+1, .inr (e,k) => .inr (e, fun o => (k o).map (promote h))

variable [DecidableEq X] [Fintype O] [DecidableEq O]

omit [Fintype O] in
theorem promote_valid (M : Model X E O C R) (h : ℕ) (V : Finset X) (t : Tree E O C h) :
    M.Valid (h+1) V (promote h t) ↔ M.Valid h V t := by
  induction h generalizing V with
  | zero => rfl
  | succ h ih =>
    cases t with
    | inl c => rfl
    | inr ek =>
      obtain ⟨e,k⟩ := ek
      change (M.Allowed V e ∧ _) ↔ (M.Allowed V e ∧ _)
      apply and_congr_right
      intro _
      apply forall_congr'
      intro o
      cases he : k o with
      | none => simp only [he,Option.map_none]
      | some child => simpa only [he,Option.map_some] using ih (M.update V e o) child

theorem promote_profile (M : Model X E O C R) (h : ℕ) (V : Finset X) (t : Tree E O C h) :
    M.profile (h+1) V (promote h t) = M.profile h V t := by
  induction h generalizing V with
  | zero => rfl
  | succ h ih =>
    cases t with
    | inl c => rfl
    | inr ek =>
      obtain ⟨e,k⟩ := ek
      change M.nodeProfile e _ = M.nodeProfile e _
      congr 1
      funext o
      cases he : k o with
      | none => simp only [he,Option.map_none]
      | some child => simp only [he,Option.map_some,ih]

theorem pad_horizon (M : Model X E O C R) (h n : ℕ) (V : Finset X) (t : Tree E O C h)
    (ht : M.Valid h V t) : ∃ u : Tree E O C (h+n), M.Valid (h+n) V u ∧ M.profile (h+n) V u = M.profile h V t := by
  induction n with
  | zero => exact ⟨t,ht,rfl⟩
  | succ n ih =>
    obtain ⟨u,hu,he⟩ := ih
    exact ⟨promote (h+n) u, (M.promote_valid _ _ _).mpr hu, (M.promote_profile _ _ _).trans he⟩

variable [Fintype E] [Fintype C] [Fintype R]

/-- A finite closed backup table supplies lower bounds at EVERY horizon. -/
theorem closed_family_dominates (M : Model X E O C R) (F : Finset X → Finset (Profile R))
    (closed : ∀ V, prune (M.backup F V) = F V) (h : ℕ) (V : Finset X) (t : Tree E O C h)
    (ht : M.Valid h V t) : ∃ p ∈ F V, p ≤ M.profile h V t := by
  induction h generalizing V with
  | zero =>
    have hm : (M.terminalCost t V,1) ∈ M.backup F V :=
      (M.mem_backup F V _).mpr (Or.inl ((M.mem_stops V _).mpr ⟨t,ht,rfl⟩))
    obtain ⟨p,hp,hle⟩ := HardPareto.exists_frontier_le _ hm
    rw [← prune_eq_frontier,closed] at hp
    exact ⟨p,hp,hle⟩
  | succ h ih =>
    obtain ⟨p,hp,hle⟩ := M.backup_dominates h F ih V t ht
    obtain ⟨q,hq,hqp⟩ := HardPareto.exists_frontier_le _ hp
    rw [← prune_eq_frontier,closed] at hq
    exact ⟨q,hq,hqp.trans hle⟩

/-- A closed family is an antichain at each support. -/
theorem closed_family_antichain (M : Model X E O C R) (F : Finset X → Finset (Profile R))
    (closed : ∀ V, prune (M.backup F V) = F V) (V : Finset X)
    {p q : Profile R} (hp : p ∈ F V) (hq : q ∈ F V) (hqp : q ≤ p) : p ≤ q := by
  have hf : HardPareto.frontier (M.backup F V) = F V := by rw [← prune_eq_frontier,closed]
  rw [← hf] at hp hq
  exact ((HardPareto.mem_frontier _ _).mp hp).2 q (HardPareto.frontier_subset _ hq) hqp

/-- Once its retained profiles are realizable, a closed table is the exact frontier. -/
theorem closed_family_exact (M : Model X E O C R) (F : Finset X → Finset (Profile R))
    (closed : ∀ V, prune (M.backup F V) = F V) (h : ℕ) (V : Finset X)
    (witness : ∀ p ∈ F V, ∃ t : Tree E O C h, M.Valid h V t ∧ M.profile h V t = p) :
    M.solve h V = F V := by
  ext p
  rw [M.exact_frontier]
  constructor
  · rintro ⟨⟨t,ht,he⟩,hmin⟩
    obtain ⟨q,hq,hqt⟩ := M.closed_family_dominates F closed h V t ht
    rw [he] at hqt
    obtain ⟨u,hu,hue⟩ := witness q hq
    have hpq : p ≤ q := by simpa only [hue] using hmin u hu (by simpa only [hue] using hqt)
    exact (le_antisymm hpq hqt) ▸ hq
  · intro hp
    refine ⟨witness p hp,?_⟩
    intro t ht htp
    obtain ⟨q,hq,hqt⟩ := M.closed_family_dominates F closed h V t ht
    exact (M.closed_family_antichain F closed V hp hq (hqt.trans htp)).trans hqt

omit [Fintype O] [Fintype E] [Fintype C] [Fintype R] in
/-- Strictly possible reports are exactly the stored children of a valid query. -/
theorem valid_child (M : Model X E O C R) {h : ℕ} {V : Finset X}
    {e : E} {k : O → Option (Tree E O C h)} (hv : M.Valid (h+1) V (.inr (e,k))) (o : O) :
    (M.update V e o).Nonempty ↔ ∃ t, k o = some t ∧ M.Valid h (M.update V e o) t := by
  constructor
  · intro hn
    cases he : k o with
    | none =>
      have hz : M.update V e o = ∅ := by simpa only [he] using hv.2 o
      exact False.elim (hn.ne_empty hz)
    | some t => exact ⟨t,rfl,by simpa only [he] using hv.2 o⟩
  · rintro ⟨t,_,ht⟩
    exact M.valid_nonempty ht

/-- Stronger than merely bounding terminal work: each coordinate is its exact maximum. -/
def ExactCharges (M : Model X E O C R) (charge : C → X → R → ℕ) : Prop :=
  ∀ c V r, M.terminalCost c V r = V.sup (fun x => charge c x r)

omit [DecidableEq X] [Fintype E] [Fintype O] [DecidableEq O] [Fintype C] [Fintype R] in
 theorem ExactCharges.bounded {M : Model X E O C R} {charge : C → X → R → ℕ}
    (h : M.ExactCharges charge) : M.ChargesBounded charge := by
  intro c V x hx r
  rw [h c V r]
  exact Finset.le_sup (f := fun x => charge c x r) hx

omit [Fintype E] [Fintype C] [Fintype R] in
/-- Each online coordinate has a realizing initial case. Different coordinates may use different cases. -/
theorem worst_coordinate_attained (M : Model X E O C R) (charge : C → X → R → ℕ)
    (hc : M.ExactCharges charge) (h : ℕ) (V : Finset X) (t : Tree E O C h)
    (hv : M.Valid h V t) (j : R) :
    ∃ x ∈ V, ∃ r, M.execute charge h t x = some r ∧ r.cost j = (M.profile h V t).1 j := by
  induction h generalizing V with
  | zero =>
    obtain ⟨x,hx,he⟩ := V.exists_mem_eq_sup hv.1 (fun x => charge t x j)
    exact ⟨x,hx,⟨x,t,charge t x,[]⟩,rfl,he.symm.trans (hc t V j).symm⟩
  | succ h ih =>
    cases t with
    | inl c =>
      obtain ⟨x,hx,he⟩ := V.exists_mem_eq_sup hv.1 (fun x => charge c x j)
      exact ⟨x,hx,⟨x,c,charge c x,[]⟩,rfl,he.symm.trans (hc c V j).symm⟩
    | inr ek =>
      obtain ⟨e,k⟩ := ek
      let live : Finset O := univ.filter (fun o => (M.update V e o).Nonempty)
      let f : O → ℕ := fun o => (optional ((k o).map (M.profile h (M.update V e o)))).1 j
      have hn : live.Nonempty := by
        obtain ⟨x,hx⟩ := hv.1.1
        exact ⟨M.observe e x, mem_filter.mpr ⟨mem_univ _, ⟨_,M.actual_next_mem hx e⟩⟩⟩
      have he : univ.sup f = live.sup f := by
        apply le_antisymm
        · apply Finset.sup_le
          intro o _
          by_cases hl : (M.update V e o).Nonempty
          · exact Finset.le_sup (f := f) (mem_filter.mpr ⟨mem_univ _,hl⟩)
          · have hz : k o = none := by
              cases ho : k o with
              | none => rfl
              | some c => exact False.elim (hl ((M.valid_child hv o).mpr ⟨c,ho,by simpa only [ho] using hv.2 o⟩))
            simp [f,hz,optional]
        · apply Finset.sup_le
          intro o _
          exact Finset.le_sup (f := f) (mem_univ o)
      obtain ⟨o,ho,hmax⟩ := live.exists_mem_eq_sup hn f
      obtain ⟨child,hchild,hvalid⟩ := (M.valid_child hv o).mp (mem_filter.mp ho).2
      obtain ⟨y,hy,r,hr,hcost⟩ := ih _ child hvalid
      obtain ⟨x,hx,hobs,hnext⟩ := (M.mem_update V e o y).mp hy
      have hperm := hv.1.2 x hx
      refine ⟨x,hx,M.prepend e o r,?_,?_⟩
      · simp only [execute,hperm,ite_true,hobs,hchild,Option.bind_some,hnext,hr,Option.map_some]
      · change M.stepCost e j + r.cost j = M.stepCost e j + univ.sup f
        rw [hcost,he,hmax]
        simp only [f,hchild,Option.map_some,optional,Option.getD_some]

end Model
end Komorebi.MachineTheory.HardInquiry
