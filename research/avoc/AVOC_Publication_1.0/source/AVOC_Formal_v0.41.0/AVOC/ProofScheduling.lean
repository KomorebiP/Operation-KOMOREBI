import Mathlib.Order.Preorder.Finite
import Mathlib.Data.Finset.Card
import Mathlib.Data.Finset.Powerset
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Order.Antichain

namespace Komorebi.AVOC.Scheduling

variable {P : Type*} [PartialOrder P] [DecidableEq P]

/-- A completed set contains every declared prerequisite. This is a scheduling
invariant, not a proof that the claims themselves are true. -/
def IsIdeal (K : Finset P) : Prop :=
  ∀ ⦃x⦄, x ∈ K → ∀ ⦃y⦄, y ≤ x → y ∈ K

/-- A fresh task is ready precisely when all strict prerequisites are complete. -/
def Ready (K : Finset P) (x : P) : Prop :=
  x ∉ K ∧ ∀ y, y < x → y ∈ K

/-- Simultaneous tasks are incomparable in the transitive dependency order. -/
def Antichain (B : Finset P) : Prop :=
  ∀ ⦃x⦄, x ∈ B → ∀ ⦃y⦄, y ∈ B → x ≤ y → x = y

omit [DecidableEq P] in
theorem ideal_empty : IsIdeal (∅ : Finset P) := by
  intro x hx
  simp at hx

theorem ideal_union {K L : Finset P} (hK : IsIdeal K) (hL : IsIdeal L) :
    IsIdeal (K ∪ L) := by
  intro x hx y hy
  rcases Finset.mem_union.mp hx with hx | hx
  · exact Finset.mem_union_left _ (hK hx hy)
  · exact Finset.mem_union_right _ (hL hx hy)

theorem ideal_insert {K : Finset P} {x : P}
    (hK : IsIdeal K) (hx : Ready K x) : IsIdeal (insert x K) := by
  intro y hy z hz
  rcases Finset.mem_insert.mp hy with heq | hy
  · subst y
    by_cases heq : z = x
    · exact Finset.mem_insert.mpr (Or.inl heq)
    · exact Finset.mem_insert.mpr (Or.inr (hx.2 z (lt_of_le_of_ne hz heq)))
  · exact Finset.mem_insert.mpr (Or.inr (hK hy hz))

theorem ready_iff_ideal_insert {K : Finset P} {x : P}
    (hK : IsIdeal K) (hx : x ∉ K) :
    Ready K x ↔ IsIdeal (insert x K) := by
  constructor
  · exact ideal_insert hK
  · intro hi
    refine ⟨hx, ?_⟩
    intro y hy
    have hm := hi (Finset.mem_insert_self x K) (le_of_lt hy)
    rcases Finset.mem_insert.mp hm with heq | hm
    · exact False.elim ((ne_of_lt hy) heq)
    · exact hm

omit [DecidableEq P] in
theorem ready_incomparable {K : Finset P} {x y : P}
    (hx : Ready K x) (hy : Ready K y) (hxy : x ≤ y) : x = y := by
  by_contra hne
  exact hx.1 (hy.2 x (lt_of_le_of_ne hxy hne))

theorem ready_persists {K : Finset P} {x y : P}
    (hy : Ready K y) (hne : y ≠ x) : Ready (insert x K) y := by
  constructor
  · simpa [Finset.mem_insert] using And.intro hne hy.1
  · intro z hz
    exact Finset.mem_insert_of_mem (hy.2 z hz)

/-- The frontier is only about readiness, not success probability or elapsed time. -/
noncomputable def frontier [Fintype P] (K : Finset P) : Finset P := by
  classical
  exact Finset.univ.filter (fun x => Ready K x)

omit [DecidableEq P] in
@[simp] theorem mem_frontier [Fintype P] {K : Finset P} {x : P} :
    x ∈ frontier K ↔ Ready K x := by
  classical
  simp [frontier]

omit [DecidableEq P] in
theorem frontier_antichain [Fintype P] (K : Finset P) : Antichain (frontier K) := by
  intro x hx y hy hxy
  exact ready_incomparable (mem_frontier.mp hx) (mem_frontier.mp hy) hxy

omit [DecidableEq P] in
theorem frontier_disjoint [Fintype P] (K : Finset P) : Disjoint K (frontier K) := by
  apply Finset.disjoint_left.mpr
  intro x hx hxf
  exact (mem_frontier.mp hxf).1 hx

omit [DecidableEq P] in
theorem antichain_subset {B C : Finset P} (hC : Antichain C) (hsub : B ⊆ C) :
    Antichain B := by
  intro x hx y hy hxy
  exact hC (hsub hx) (hsub hy) hxy

theorem frontier_batch_ideal [Fintype P] {K B : Finset P}
    (hK : IsIdeal K) (hB : B ⊆ frontier K) : IsIdeal (K ∪ B) := by
  intro x hx y hy
  rcases Finset.mem_union.mp hx with hx | hx
  · exact Finset.mem_union_left _ (hK hx hy)
  · by_cases heq : y = x
    · subst y
      exact Finset.mem_union_right _ hx
    · exact Finset.mem_union_left _ ((mem_frontier.mp (hB hx)).2 y
        (lt_of_le_of_ne hy heq))

/-- Simultaneous legality requires all three conditions, not merely antichainhood. -/
theorem batch_iff [Fintype P] {K B : Finset P} (hK : IsIdeal K) :
    B ⊆ frontier K ↔
      Disjoint K B ∧ Antichain B ∧ IsIdeal (K ∪ B) := by
  constructor
  · intro hB
    refine ⟨?_, antichain_subset (frontier_antichain K) hB,
      frontier_batch_ideal hK hB⟩
    apply Finset.disjoint_left.mpr
    intro x hx hxb
    exact (mem_frontier.mp (hB hxb)).1 hx
  · rintro ⟨hd, ha, hi⟩ x hx
    apply mem_frontier.mpr
    refine ⟨?_, ?_⟩
    · intro hxk
      exact Finset.disjoint_left.mp hd hxk hx
    · intro y hy
      have hm := hi (Finset.mem_union_right K hx) (le_of_lt hy)
      rcases Finset.mem_union.mp hm with hm | hm
      · exact hm
      · exact False.elim ((ne_of_lt hy) (ha hm hx (le_of_lt hy)))

theorem batch_card_add [Fintype P] {K B : Finset P} (hB : B ⊆ frontier K) :
    (K ∪ B).card = K.card + B.card := by
  apply Finset.card_union_of_disjoint
  apply Finset.disjoint_left.mpr
  intro x hx hxb
  exact (mem_frontier.mp (hB hxb)).1 hx

/-- Poset width as a finite maximum over all antichains. -/
noncomputable def width [Fintype P] : Nat := by
  classical
  exact (Finset.univ.powerset.filter (fun B : Finset P => Antichain B)).sup Finset.card

omit [DecidableEq P] in
theorem antichain_card_le_width [Fintype P] {B : Finset P} (hB : Antichain B) :
    B.card ≤ width (P := P) := by
  classical
  unfold width
  apply Finset.le_sup (f := Finset.card)
  simp only [Finset.mem_filter, Finset.mem_powerset, Finset.subset_univ, true_and]
  exact hB

omit [DecidableEq P] in
theorem frontier_card_le_width [Fintype P] (K : Finset P) :
    (frontier K).card ≤ width (P := P) :=
  antichain_card_le_width (frontier_antichain K)

omit [DecidableEq P] in
theorem batch_card_le_frontier [Fintype P] {K B : Finset P} (hB : B ⊆ frontier K) :
    B.card ≤ (frontier K).card := Finset.card_le_card hB

omit [DecidableEq P] in
theorem batch_card_le_width [Fintype P] {K B : Finset P} (hB : B ⊆ frontier K) :
    B.card ≤ width (P := P) :=
  le_trans (batch_card_le_frontier hB) (frontier_card_le_width K)

/-- A fixed baseline is processed sequentially; each entry is completed once. -/
def Legal : Finset P → List P → Prop
  | _, [] => True
  | K, x :: xs => Ready K x ∧ Legal (insert x K) xs

@[simp] theorem legal_nil (K : Finset P) : Legal K [] := True.intro

@[simp] theorem legal_cons (K : Finset P) (x : P) (xs : List P) :
    Legal K (x :: xs) ↔ Ready K x ∧ Legal (insert x K) xs := Iff.rfl

theorem legal_final_ideal {K : Finset P} {xs : List P}
    (hK : IsIdeal K) (hl : Legal K xs) : IsIdeal (K ∪ xs.toFinset) := by
  induction xs generalizing K with
  | nil => simpa using hK
  | cons x xs ih =>
    have ht := ih (ideal_insert hK hl.1) hl.2
    simpa [List.toFinset_cons, Finset.insert_union, Finset.union_insert] using ht

theorem legal_fresh {K : Finset P} {xs : List P}
    (hl : Legal K xs) : ∀ x ∈ xs, x ∉ K := by
  induction xs generalizing K with
  | nil => simp
  | cons x xs ih =>
    intro y hy
    rcases List.mem_cons.mp hy with rfl | hy
    · exact hl.1.1
    · intro hyk
      exact ih hl.2 y hy (Finset.mem_insert_of_mem hyk)

theorem legal_nodup {K : Finset P} {xs : List P}
    (hl : Legal K xs) : xs.Nodup := by
  induction xs generalizing K with
  | nil => simp
  | cons x xs ih =>
    apply List.nodup_cons.mpr
    refine ⟨?_, ih hl.2⟩
    intro hx
    exact legal_fresh hl.2 x hx (Finset.mem_insert_self x K)

theorem legal_topological {K : Finset P} {xs : List P}
    (hl : Legal K xs) : xs.Pairwise (fun x y => ¬ y < x) := by
  induction xs generalizing K with
  | nil => exact List.Pairwise.nil
  | cons x xs ih =>
    apply List.pairwise_cons.mpr
    refine ⟨?_, ih hl.2⟩
    intro y hy hyx
    exact legal_fresh hl y (List.mem_cons_of_mem x hy) (hl.1.2 y hyx)

end Komorebi.AVOC.Scheduling
