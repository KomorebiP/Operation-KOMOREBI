import MachineTheory.HardPareto
import Mathlib.Data.Fintype.Option
import Mathlib.Data.Fintype.Sum
import Mathlib.Data.Fintype.Prod
import Mathlib.Data.Finset.Union

/-!
# Hard-budget finite inquiry

Core 5.1. A literal tree uses `none` for an impossible report and an actual child
for every possible report. The validity predicate rejects both missing reachable
children and invented unreachable children. It evaluates the actual post-action
support. Costs have named natural-number coordinates; storage counts ALL nodes.
-/
namespace Komorebi.MachineTheory.HardInquiry

open Finset

variable {X E O C R : Type}

/-- Boolean guards specify finite decision tables, not an unverified host checker. -/
structure Model (X E O C R : Type) where
  permitted : E → X → Bool
  next : E → X → X
  observe : E → X → O
  accept : X → C → Bool
  stepCost : E → R → ℕ
  terminalCost : C → Finset X → R → ℕ

/-- A profile pairs online costs in every named coordinate with complete storage. -/
abbrev Profile (R : Type) := (R → ℕ) × ℕ

/-- An option contains a real subtree or no stored subtree at all. -/
def Tree (E O C : Type) : ℕ → Type
  | 0 => C
  | h + 1 => C ⊕ (E × (O → Option (Tree E O C h)))

variable [DecidableEq X] [Fintype E]
  [Fintype O] [DecidableEq O] [Fintype C]
  [Fintype R]

namespace Model

/-- Images, not pre-action supports, define the next information state. -/
def update (M : Model X E O C R) (V : Finset X) (e : E) (o : O) : Finset X :=
  (V.filter (fun x => M.observe e x = o)).image (M.next e)

omit [Fintype E] [Fintype O] [Fintype C] [Fintype R] in
theorem mem_update (M : Model X E O C R) (V : Finset X) (e : E) (o : O) (y : X) :
    y ∈ M.update V e o ↔ ∃ x ∈ V, M.observe e x = o ∧ M.next e x = y := by
  simp only [update, mem_image, mem_filter]
  constructor
  · rintro ⟨x, ⟨hx, ho⟩, hy⟩; exact ⟨x, hx, ho, hy⟩
  · rintro ⟨x, hx, ho, hy⟩; exact ⟨x, ⟨hx, ho⟩, hy⟩

omit [Fintype E] [Fintype O] [Fintype C] [Fintype R] in
theorem actual_next_mem (M : Model X E O C R) {V : Finset X} {x : X}
    (hx : x ∈ V) (e : E) : M.next e x ∈ M.update V e (M.observe e x) :=
  (M.mem_update _ _ _ _).mpr ⟨x, hx, rfl, rfl⟩

def Allowed (M : Model X E O C R) (V : Finset X) (e : E) : Prop :=
  V.Nonempty ∧ ∀ x ∈ V, M.permitted e x = true

def Terminal (M : Model X E O C R) (V : Finset X) (c : C) : Prop :=
  V.Nonempty ∧ ∀ x ∈ V, M.accept x c = true

instance allowedDecidable (M : Model X E O C R) (V : Finset X) (e : E) :
    Decidable (M.Allowed V e) := inferInstanceAs (Decidable (_ ∧ _))
instance terminalDecidable (M : Model X E O C R) (V : Finset X) (c : C) :
    Decidable (M.Terminal V c) := inferInstanceAs (Decidable (_ ∧ _))

/-- Validity uses only a common experiment/terminal label, never a hidden-state selector. -/
def Valid (M : Model X E O C R) : (h : ℕ) → Finset X → Tree E O C h → Prop
  | 0, V, c => M.Terminal V c
  | _ + 1, V, .inl c => M.Terminal V c
  | h + 1, V, .inr (e, k) => M.Allowed V e ∧ ∀ o,
      match k o with
      | none => M.update V e o = ∅
      | some t => M.Valid h (M.update V e o) t

/-- Total finite validation of an explicit stored tree. -/
instance validDecidable (M : Model X E O C R) :
    (h : ℕ) → (V : Finset X) → (t : Tree E O C h) → Decidable (M.Valid h V t)
  | 0, V, c => M.terminalDecidable V c
  | _+1, V, .inl c => M.terminalDecidable V c
  | h+1, V, .inr (e,k) => by
      letI : ∀ o, Decidable (match k o with
          | none => M.update V e o = ∅
          | some t => M.Valid h (M.update V e o) t) := fun o =>
        match k o with
        | none => inferInstance
        | some t => M.validDecidable h (M.update V e o) t
      exact inferInstanceAs (Decidable (M.Allowed V e ∧ ∀ o,
        match k o with
        | none => M.update V e o = ∅
        | some t => M.Valid h (M.update V e o) t))

omit [Fintype E] [Fintype O] [Fintype C] [Fintype R] in
theorem valid_nonempty (M : Model X E O C R) {h : ℕ} {V : Finset X} {t : Tree E O C h}
    (hv : M.Valid h V t) : V.Nonempty := by
  cases h with
  | zero => exact hv.1
  | succ h => cases t with
    | inl c => exact hv.1
    | inr ek => exact hv.1.1

/-- Nonexistent children contribute zero storage and zero cost, not a free success. -/
def optional (p : Option (Profile R)) : Profile R := p.getD (0, 0)

def nodeProfile (M : Model X E O C R) (e : E) (k : O → Option (Profile R)) : Profile R :=
  (fun r => M.stepCost e r + univ.sup (fun o => (optional (k o)).1 r),
    1 + ∑ o, (optional (k o)).2)

def profile (M : Model X E O C R) : (h : ℕ) → Finset X → Tree E O C h → Profile R
  | 0, V, c => (M.terminalCost c V, 1)
  | _ + 1, V, .inl c => (M.terminalCost c V, 1)
  | h + 1, V, .inr (e, k) => M.nodeProfile e
      (fun o => (k o).map (M.profile h (M.update V e o)))

omit [Fintype E] [Fintype C] [Fintype R] in
theorem records_positive (M : Model X E O C R) (h : ℕ) (V : Finset X) (t : Tree E O C h) :
    1 ≤ (M.profile h V t).2 := by
  cases h with
  | zero => exact le_rfl
  | succ h => cases t with
    | inl c => exact le_rfl
    | inr ek => exact Nat.le_add_right _ _

omit [DecidableEq X] [Fintype E] [DecidableEq O] [Fintype C] [Fintype R] in
theorem nodeProfile_mono (M : Model X E O C R) (e : E)
    (k l : O → Option (Profile R)) (hle : ∀ o, optional (k o) ≤ optional (l o)) :
    M.nodeProfile e k ≤ M.nodeProfile e l := by
  constructor
  · intro r
    apply Nat.add_le_add_left
    apply Finset.sup_le
    intro o _
    exact ((hle o).1 r).trans (Finset.le_sup (f := fun o => (optional (l o)).1 r) (mem_univ o))
  · exact Nat.add_le_add_left (Finset.sum_le_sum (fun o _ => (hle o).2)) 1

/-- All acceptable terminal profiles at this support. -/
def stops (M : Model X E O C R) (V : Finset X) : Finset (Profile R) :=
  (univ.filter (M.Terminal V)).image (fun c => (M.terminalCost c V, 1))

omit [DecidableEq X] [Fintype E] [Fintype O] [DecidableEq O] in
@[simp] theorem mem_stops (M : Model X E O C R) (V : Finset X) (p : Profile R) :
    p ∈ M.stops V ↔ ∃ c, M.Terminal V c ∧ (M.terminalCost c V, 1) = p := by
  simp [stops]

/-- Each report independently chooses one achievable child, unless it is impossible. -/
def options (M : Model X E O C R) (F : Finset X → Finset (Profile R))
    (V : Finset X) (e : E) (o : O) : Finset (Option (Profile R)) :=
  if (M.update V e o).Nonempty then (F (M.update V e o)).image some else {none}

/-- One unpruned backup; the input family may already have been Pareto reduced. -/
def backup (M : Model X E O C R) (F : Finset X → Finset (Profile R))
    (V : Finset X) : Finset (Profile R) :=
  M.stops V ∪ univ.biUnion (fun e => if M.Allowed V e then
    (Fintype.piFinset (M.options F V e)).image (M.nodeProfile e) else ∅)

@[simp] theorem mem_backup (M : Model X E O C R) (F : Finset X → Finset (Profile R))
    (V : Finset X) (p : Profile R) :
    p ∈ M.backup F V ↔ p ∈ M.stops V ∨ ∃ e, M.Allowed V e ∧
      ∃ k : O → Option (Profile R), (∀ o, k o ∈ M.options F V e o) ∧ M.nodeProfile e k = p := by
  simp only [backup, mem_union, mem_biUnion, mem_univ, true_and]
  constructor
  · rintro (hs | ⟨e, he⟩)
    · exact Or.inl hs
    · by_cases ha : M.Allowed V e
      · simp only [ha, ite_true, mem_image, Fintype.mem_piFinset] at he
        exact Or.inr ⟨e, ha, he⟩
      · simp [ha] at he
  · rintro (hs | ⟨e, ha, k, hk, hp⟩)
    · exact Or.inl hs
    · exact Or.inr ⟨e, by simp only [ha, ite_true, mem_image, Fintype.mem_piFinset]; exact ⟨k, hk, hp⟩⟩

noncomputable def solve (M : Model X E O C R) : ℕ → Finset X → Finset (Profile R)
  | 0, V => HardPareto.frontier (M.stops V)
  | h + 1, V => HardPareto.frontier (M.backup (M.solve h) V)

/-- Soundness of one backup includes a complete concrete observation tree. -/
theorem backup_witness (M : Model X E O C R) (h : ℕ)
    (F : Finset X → Finset (Profile R))
    (sound : ∀ V p, p ∈ F V → ∃ t : Tree E O C h, M.Valid h V t ∧ M.profile h V t = p)
    (V : Finset X) (p : Profile R) (hp : p ∈ M.backup F V) :
    ∃ t : Tree E O C (h+1), M.Valid (h+1) V t ∧ M.profile (h+1) V t = p := by
  classical
  rcases (M.mem_backup F V p).mp hp with hs | ⟨e, ha, k, hk, he⟩
  · obtain ⟨c, hc, he⟩ := (M.mem_stops V p).mp hs
    exact ⟨.inl c, hc, he⟩
  · have hw : ∀ o, ∃ t : Option (Tree E O C h),
        (match t with | none => M.update V e o = ∅ | some t => M.Valid h (M.update V e o) t) ∧
        t.map (M.profile h (M.update V e o)) = k o := by
      intro o
      by_cases hn : (M.update V e o).Nonempty
      · have hm := hk o
        simp only [options, hn, ite_true, mem_image] at hm
        obtain ⟨q, hq, hko⟩ := hm
        obtain ⟨t, hv, ht⟩ := sound _ q hq
        exact ⟨some t, hv, by simpa only [Option.map_some, ht] using hko⟩
      · have hm : k o = none := by simpa [options, hn] using hk o
        exact ⟨none, Finset.not_nonempty_iff_eq_empty.mp hn, by simp [hm]⟩
    let t : O → Option (Tree E O C h) := fun o => (hw o).choose
    have hv : ∀ o, (match t o with | none => M.update V e o = ∅ | some t => M.Valid h (M.update V e o) t) :=
      fun o => (hw o).choose_spec.1
    have ht : (fun o => (t o).map (M.profile h (M.update V e o))) = k :=
      funext (fun o => (hw o).choose_spec.2)
    refine ⟨.inr (e,t), ⟨ha,hv⟩, ?_⟩
    change M.nodeProfile e _ = p
    rw [ht, he]

/-- A dominating child replacement can be chosen at every actual branch simultaneously. -/
theorem backup_dominates (M : Model X E O C R) (h : ℕ)
    (F : Finset X → Finset (Profile R))
    (complete : ∀ V (t : Tree E O C h), M.Valid h V t → ∃ p ∈ F V, p ≤ M.profile h V t)
    (V : Finset X) (t : Tree E O C (h+1)) (hv : M.Valid (h+1) V t) :
    ∃ p ∈ M.backup F V, p ≤ M.profile (h+1) V t := by
  classical
  cases t with
  | inl c => exact ⟨_, (M.mem_backup F V _).mpr (Or.inl ((M.mem_stops V _).mpr ⟨c,hv,rfl⟩)), le_rfl⟩
  | inr ek =>
    obtain ⟨e,k⟩ := ek
    obtain ⟨ha,hk⟩ := hv
    have hw : ∀ o, ∃ p ∈ M.options F V e o,
        optional p ≤ optional ((k o).map (M.profile h (M.update V e o))) := by
      intro o
      cases heq : k o with
      | none =>
        have hz : M.update V e o = ∅ := by simpa only [heq] using hk o
        exact ⟨none, by simp [options,hz], by simp⟩
      | some t =>
        have ht : M.Valid h (M.update V e o) t := by simpa only [heq] using hk o
        have hn := M.valid_nonempty ht
        obtain ⟨p,hp,hle⟩ := complete _ t ht
        exact ⟨some p, by simp only [options,hn,ite_true,mem_image]; exact ⟨p,hp,rfl⟩,
          by simpa [heq,optional] using hle⟩
    let p : O → Option (Profile R) := fun o => (hw o).choose
    refine ⟨M.nodeProfile e p, (M.mem_backup F V _).mpr (Or.inr ⟨e,ha,p,?_,rfl⟩), ?_⟩
    · exact fun o => (hw o).choose_spec.1
    · exact M.nodeProfile_mono e p _ (fun o => (hw o).choose_spec.2)

/-- The dynamic program is sound and lower-cofinal in ALL valid tree profiles. -/
theorem solve_correct (M : Model X E O C R) (h : ℕ) :
    (∀ V p, p ∈ M.solve h V → ∃ t : Tree E O C h, M.Valid h V t ∧ M.profile h V t = p) ∧
    (∀ V (t : Tree E O C h), M.Valid h V t → ∃ p ∈ M.solve h V, p ≤ M.profile h V t) := by
  induction h with
  | zero =>
    constructor
    · intro V p hp
      obtain ⟨c,hc,he⟩ := (M.mem_stops V p).mp (HardPareto.frontier_subset _ hp)
      exact ⟨c,hc,he⟩
    · intro V c hc
      exact HardPareto.exists_frontier_le _ ((M.mem_stops V _).mpr ⟨c,hc,rfl⟩)
  | succ h ih =>
    constructor
    · intro V p hp
      exact M.backup_witness h (M.solve h) ih.1 V p (HardPareto.frontier_subset _ hp)
    · intro V t ht
      obtain ⟨p,hp,hle⟩ := M.backup_dominates h (M.solve h) ih.2 V t ht
      obtain ⟨q,hq,hqp⟩ := HardPareto.exists_frontier_le _ hp
      exact ⟨q,hq,hqp.trans hle⟩

theorem solve_witness (M : Model X E O C R) (h : ℕ) (V : Finset X) (p : Profile R)
    (hp : p ∈ M.solve h V) : ∃ t : Tree E O C h, M.Valid h V t ∧ M.profile h V t = p :=
  (M.solve_correct h).1 V p hp

theorem solve_dominates (M : Model X E O C R) (h : ℕ) (V : Finset X) (t : Tree E O C h)
    (ht : M.Valid h V t) : ∃ p ∈ M.solve h V, p ≤ M.profile h V t :=
  (M.solve_correct h).2 V t ht

theorem solve_antichain (M : Model X E O C R) (h : ℕ) (V : Finset X)
    {p q : Profile R} (hp : p ∈ M.solve h V) (hq : q ∈ M.solve h V) (hqp : q ≤ p) : p ≤ q := by
  cases h with
  | zero => exact ((HardPareto.mem_frontier _ _).mp hp).2 q (HardPareto.frontier_subset _ hq) hqp
  | succ h => exact ((HardPareto.mem_frontier _ _).mp hp).2 q (HardPareto.frontier_subset _ hq) hqp

/-- Core 5.1: EXACT nondominated profiles, not an upper approximation or separate optima. -/
theorem exact_frontier (M : Model X E O C R) (h : ℕ) (V : Finset X) (p : Profile R) :
    p ∈ M.solve h V ↔
      (∃ t : Tree E O C h, M.Valid h V t ∧ M.profile h V t = p) ∧
      ∀ t : Tree E O C h, M.Valid h V t → M.profile h V t ≤ p → p ≤ M.profile h V t := by
  constructor
  · intro hp
    refine ⟨M.solve_witness h V p hp, ?_⟩
    intro t ht htp
    obtain ⟨q,hq,hqt⟩ := M.solve_dominates h V t ht
    exact (M.solve_antichain h V hp hq (hqt.trans htp)).trans hqt
  · rintro ⟨⟨t,ht,he⟩,hmin⟩
    obtain ⟨q,hq,hqt⟩ := M.solve_dominates h V t ht
    rw [he] at hqt
    obtain ⟨s,hs,hse⟩ := M.solve_witness h V q hq
    have hpq : p ≤ q := by simpa only [hse] using hmin s hs (by simpa only [hse] using hqt)
    exact (le_antisymm hpq hqt) ▸ hq

/-- One online vector and one storage bound must be met by the SAME tree. -/
theorem joint_budget_iff (M : Model X E O C R) (h : ℕ) (V : Finset X) (b : Profile R) :
    (∃ t : Tree E O C h, M.Valid h V t ∧ M.profile h V t ≤ b) ↔
      ∃ p ∈ M.solve h V, p ≤ b := by
  constructor
  · rintro ⟨t,ht,hb⟩
    obtain ⟨p,hp,hpt⟩ := M.solve_dominates h V t ht
    exact ⟨p,hp,hpt.trans hb⟩
  · rintro ⟨p,hp,hb⟩
    obtain ⟨t,ht,he⟩ := M.solve_witness h V p hp
    exact ⟨t,ht,by simpa only [he] using hb⟩

/-- Exhaustion is complete only within the actual finite model and horizon. -/
theorem no_tree_iff_empty (M : Model X E O C R) (h : ℕ) (V : Finset X) :
    (¬ ∃ t : Tree E O C h, M.Valid h V t) ↔ M.solve h V = ∅ := by
  constructor
  · intro ht
    apply Finset.eq_empty_iff_forall_notMem.mpr
    intro p hp
    obtain ⟨t,hv,_⟩ := M.solve_witness h V p hp
    exact ht ⟨t,hv⟩
  · intro he ⟨t,ht⟩
    obtain ⟨p,hp,_⟩ := M.solve_dominates h V t ht
    simp only [he, Finset.notMem_empty] at hp

end Model
end Komorebi.MachineTheory.HardInquiry
