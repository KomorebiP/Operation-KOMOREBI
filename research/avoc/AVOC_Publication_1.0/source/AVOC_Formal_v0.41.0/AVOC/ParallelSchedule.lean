import AVOC.ScheduleCompletion
import Mathlib.Data.Fintype.Prod

namespace Komorebi.AVOC.Scheduling

variable {P : Type*} [PartialOrder P] [DecidableEq P] [Fintype P]

/-- Unit-time slots respect every strict prerequisite. -/
def RespectsDependencies (slot : P → Nat) : Prop :=
  ∀ ⦃x y⦄, x < y → slot x < slot y

noncomputable def before (slot : P → Nat) (t : Nat) : Finset P := by
  classical
  exact Finset.univ.filter (fun x => slot x < t)

noncomputable def atSlot (slot : P → Nat) (t : Nat) : Finset P := by
  classical
  exact Finset.univ.filter (fun x => slot x = t)

omit [DecidableEq P] in
theorem before_ideal {slot : P → Nat} (hs : RespectsDependencies slot) (t : Nat) :
    IsIdeal (before slot t) := by
  classical
  intro x hx y hy
  simp only [before, Finset.mem_filter, Finset.mem_univ, true_and] at hx ⊢
  by_cases he : y = x
  · simpa [he] using hx
  · exact lt_trans (hs (lt_of_le_of_ne hy he)) hx

omit [DecidableEq P] in
theorem slot_subset_frontier {slot : P → Nat} (hs : RespectsDependencies slot) (t : Nat) :
    atSlot slot t ⊆ frontier (before slot t) := by
  classical
  intro x hx
  have hxt : slot x = t := by simpa [atSlot] using hx
  apply mem_frontier.mpr
  constructor
  · simp [before, hxt]
  · intro y hy
    have hlt : slot y < t := by simpa [hxt] using hs hy
    simpa [before] using hlt

omit [DecidableEq P] in
theorem slot_card_le_width {slot : P → Nat} (hs : RespectsDependencies slot) (t : Nat) :
    (atSlot slot t).card ≤ width (P := P) :=
  batch_card_le_width (slot_subset_frontier hs t)

omit [DecidableEq P] in
/-- Distinct active workers assigned to distinct ready tasks cannot exceed the
current frontier. This does not bound workers cooperating on the same task. -/
theorem active_workers_le_frontier {W : Type*} [DecidableEq W]
    (active : Finset W) (task : W → P) (K : Finset P)
    (hready : ∀ w ∈ active, Ready K (task w))
    (hinj : ∀ w ∈ active, ∀ v ∈ active, task w = task v → w = v) :
    active.card ≤ (frontier K).card := by
  apply Finset.card_le_card_of_injOn task
  · intro w hw
    exact mem_frontier.mpr (hready w hw)
  · intro w hw v hv he
    exact hinj w hw v hv he

omit [DecidableEq P] in
theorem active_workers_le_width {W : Type*} [DecidableEq W]
    (active : Finset W) (task : W → P) (K : Finset P)
    (hready : ∀ w ∈ active, Ready K (task w))
    (hinj : ∀ w ∈ active, ∀ v ∈ active, task w = task v → w = v) :
    active.card ≤ width (P := P) :=
  le_trans (active_workers_le_frontier active task K hready hinj)
    (frontier_card_le_width K)

/-- A finite dependency chain is totally comparable. -/
def Chain (C : Finset P) : Prop :=
  ∀ ⦃x⦄, x ∈ C → ∀ ⦃y⦄, y ∈ C → x ≤ y ∨ y ≤ x

omit [DecidableEq P] [Fintype P] in
theorem chain_slot_injective {slot : P → Nat} (hs : RespectsDependencies slot)
    {C : Finset P} (hc : Chain C) : Set.InjOn slot (C : Set P) := by
  intro x hx y hy he
  by_contra hne
  rcases hc hx hy with hxy | hyx
  · have hlt := hs (lt_of_le_of_ne hxy hne)
    omega
  · have hlt := hs (lt_of_le_of_ne hyx (fun h => hne h.symm))
    omega

omit [DecidableEq P] [Fintype P] in
theorem chain_card_le_rounds {slot : P → Nat} (hs : RespectsDependencies slot)
    (rounds : Nat) (hbound : ∀ x, slot x < rounds)
    {C : Finset P} (hc : Chain C) : C.card ≤ rounds := by
  have h : C.card ≤ (Finset.range rounds).card := by
    apply Finset.card_le_card_of_injOn slot
    · intro x _
      exact Finset.mem_range.mpr (hbound x)
    · exact chain_slot_injective hs hc
  simpa using h

omit [PartialOrder P] [DecidableEq P] in
/-- One task per worker per slot gives the finite work lower bound. -/
theorem work_capacity_bound {rounds workers : Nat}
    (slot : P → Fin rounds) (worker : P → Fin workers)
    (hn : ∀ x y, slot x = slot y → worker x = worker y → x = y) :
    Fintype.card P ≤ rounds * workers := by
  let f : P → Fin rounds × Fin workers := fun x => (slot x, worker x)
  have hi : Function.Injective f := by
    intro x y he
    exact hn x y (congrArg Prod.fst he) (congrArg Prod.snd he)
  have h := Fintype.card_le_of_injective f hi
  simpa using h

end Komorebi.AVOC.Scheduling
