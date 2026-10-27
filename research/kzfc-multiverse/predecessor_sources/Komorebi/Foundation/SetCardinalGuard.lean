import Komorebi.Foundation.SetCardinalCoding
import Mathlib.SetTheory.Cardinal.Regular

/-!
# A set-quantified regular-uncountable initial-cardinal guard

The guard is independent of filter extension. Smallness is the predecessor's
set-coded injection predicate. Regularity is strict boundedness of all small
subsets, and uncountability is witnessed by an inductive member.
-/

universe u

namespace Komorebi.SetFilterCoding

open Cardinal Ordinal

/-- An ordinal with no injection into a smaller ordinal. -/
def IsInitial (K : ZFSet.{u}) : Prop :=
  K.IsOrdinal ∧ ∀ a ∈ K, ¬ SetEmbeds K a

/-- An inductive set contains zero and is closed under von Neumann successor. -/
def IsInductive (W : ZFSet.{u}) : Prop :=
  (∅ : ZFSet.{u}) ∈ W ∧ ∀ a ∈ W, insert a a ∈ W

/-- An ordinal above an inductive member is strictly above omega. -/
def HasInductiveMember (K : ZFSet.{u}) : Prop :=
  ∃ W ∈ K, IsInductive W

/-- Every small subset has a strict ordinal bound below K. -/
def SmallSubsetsBounded (K : ZFSet.{u}) : Prop :=
  ∀ S : ZFSet.{u}, S ⊆ K → SetSmall K S → ∃ b ∈ K, S ⊆ b

/-- This predicate contains no filter, compactness or residual assumption. -/
def RegularUncountableGuard (K : ZFSet.{u}) : Prop :=
  IsInitial K ∧ HasInductiveMember K ∧ SmallSubsetsBounded K

theorem isInitial_cardinal (κ : Cardinal.{u}) : IsInitial κ.ord.toZFSet := by
  refine ⟨ZFSet.isOrdinal_toZFSet _, ?_⟩
  intro a ha hi
  obtain ⟨o, ho, rfl⟩ := Ordinal.mem_toZFSet_iff.mp ha
  have hle := (setEmbeds_iff_card_le _ _).mp hi
  simp only [Ordinal.card_toZFSet, Cardinal.card_ord] at hle
  exact (Cardinal.lt_ord.mp ho).not_ge hle

theorem isInitial_iff_cardinal (K : ZFSet.{u}) :
    IsInitial K ↔ ∃ κ : Cardinal.{u}, K = κ.ord.toZFSet := by
  constructor
  · rintro ⟨ho, hmin⟩
    obtain ⟨o, rfl⟩ := ZFSet.isOrdinal_iff_mem_range_toZFSet.mp ho
    have he : o.card.ord = o := by
      apply le_antisymm (Cardinal.ord_card_le o)
      by_contra hn
      have hl : o.card.ord < o := lt_of_not_ge hn
      apply hmin o.card.ord.toZFSet (Ordinal.toZFSet_mem_toZFSet_iff.mpr hl)
      apply (setEmbeds_iff_card_le _ _).mpr
      simp
    exact ⟨o.card, congrArg Ordinal.toZFSet he.symm⟩
  · rintro ⟨κ, rfl⟩
    exact isInitial_cardinal κ

theorem nat_mem_of_inductive {W : ZFSet.{u}} (hW : IsInductive W) (n : ℕ) :
    (n : Ordinal.{u}).toZFSet ∈ W := by
  induction n with
  | zero => simpa using hW.1
  | succ n ih => simpa [Nat.cast_add, Nat.cast_one, Ordinal.toZFSet_add_one] using hW.2 _ ih

theorem omega_le_of_inductive {o : Ordinal.{u}} (h : IsInductive o.toZFSet) :
    Ordinal.omega0 ≤ o := by
  by_contra hn
  obtain ⟨n, rfl⟩ := Ordinal.lt_omega0.mp (lt_of_not_ge hn)
  exact (Ordinal.toZFSet_mem_toZFSet_iff.mp (nat_mem_of_inductive h n)).false

theorem omega_inductive : IsInductive Ordinal.omega0.{u}.toZFSet := by
  constructor
  · simpa using (Ordinal.toZFSet_mem_toZFSet_iff.mpr Ordinal.omega0_pos)
  · intro a ha
    obtain ⟨o, ho, rfl⟩ := Ordinal.mem_toZFSet_iff.mp ha
    obtain ⟨n, rfl⟩ := Ordinal.lt_omega0.mp ho
    rw [← Ordinal.toZFSet_add_one, Ordinal.toZFSet_mem_toZFSet_iff]
    simpa using Ordinal.natCast_lt_omega0 (n + 1)

theorem hasInductiveMember_initial_iff (κ : Cardinal.{u}) :
    HasInductiveMember κ.ord.toZFSet ↔ Cardinal.aleph0 < κ := by
  constructor
  · rintro ⟨W, hW, hi⟩
    obtain ⟨o, ho, rfl⟩ := Ordinal.mem_toZFSet_iff.mp hW
    have hω : Ordinal.omega0 < κ.ord := (omega_le_of_inductive hi).trans_lt ho
    simpa using Cardinal.lt_ord.mp hω
  · intro hκ
    refine ⟨Ordinal.omega0.toZFSet, ?_, omega_inductive⟩
    apply Ordinal.toZFSet_mem_toZFSet_iff.mpr
    rw [Cardinal.lt_ord]
    simpa using hκ

theorem smallSubsetsBounded_of_regular (κ : Cardinal.{u}) (hκ : κ.IsRegular) :
    SmallSubsetsBounded κ.ord.toZFSet := by
  intro S hS hs
  let f : Carrier S → Ordinal.{u} := fun s => (element S s).rank
  have hf : ∀ s, f s < κ.ord := by
    intro s
    simpa [f] using ZFSet.rank_lt_of_mem (hS (element_mem S s))
  have hcard : Cardinal.mk (Carrier S) < κ.ord.cof := by
    rw [hκ.cof_ord]
    exact (setSmall_initial_iff κ S).mp hs
  have hbound : (⨆ s, f s + 1) < κ.ord :=
    Ordinal.iSup_add_one_lt_of_lt_cof hcard hf
  refine ⟨(⨆ s, f s + 1).toZFSet, Ordinal.toZFSet_mem_toZFSet_iff.mpr hbound, ?_⟩
  intro x hx
  obtain ⟨s, rfl⟩ := exists_element S hx
  have ho := (ZFSet.isOrdinal_toZFSet κ.ord).mem (hS (element_mem S s))
  rw [← ho.toZFSet_rank_eq, Ordinal.toZFSet_mem_toZFSet_iff]
  exact (lt_add_one (f s)).trans_le (Ordinal.le_iSup (fun s => f s + 1) s)

theorem regular_of_smallSubsetsBounded (κ : Cardinal.{u}) (hκ : Cardinal.aleph0 ≤ κ)
    (hb : SmallSubsetsBounded κ.ord.toZFSet) : κ.IsRegular := by
  refine ⟨hκ, ?_⟩
  rw [← Ordinal.cof_toType]
  apply Order.le_cof_iff.mpr
  intro s hs
  by_contra hn
  have hsmall : Cardinal.mk s < κ := lt_of_not_ge hn
  let f : s → ZFSet.{u} := fun a => (Ordinal.typein (α := κ.ord.ToType) (· < ·) a.val).toZFSet
  let S : ZFSet.{u} := ZFSet.range f
  have hS : S ⊆ κ.ord.toZFSet := by
    intro x hx
    obtain ⟨a, rfl⟩ := ZFSet.mem_range.mp hx
    exact Ordinal.toZFSet_mem_toZFSet_iff.mpr (Ordinal.typein_lt_self a.val)
  have hScard : S.card < κ := by
    have hle : S.card ≤ Cardinal.mk s := by
      simpa [S] using (ZFSet.lift_card_range_le (f := f))
    exact hle.trans_lt hsmall
  obtain ⟨b, hbK, hbS⟩ := hb S hS ((setSmall_initial_iff κ S).mpr hScard)
  obtain ⟨o, ho, rfl⟩ := Ordinal.mem_toZFSet_iff.mp hbK
  obtain ⟨t, ht⟩ := Ordinal.typein_surj (α := κ.ord.ToType) (· < ·) (o := o) (by simpa using ho)
  obtain ⟨a, ha, hta⟩ := hs t
  have hlt : Ordinal.typein (α := κ.ord.ToType) (· < ·) a < o :=
    Ordinal.toZFSet_mem_toZFSet_iff.mp (hbS (ZFSet.mem_range.mpr ⟨⟨a, ha⟩, rfl⟩))
  have hle : o ≤ Ordinal.typein (α := κ.ord.ToType) (· < ·) a := by
    have h := (Ordinal.typein_le_typein' κ.ord).mpr hta
    rw [ht] at h
    exact h
  exact hlt.not_ge hle

theorem smallSubsetsBounded_initial_iff (κ : Cardinal.{u}) (hκ : Cardinal.aleph0 ≤ κ) :
    SmallSubsetsBounded κ.ord.toZFSet ↔ κ.IsRegular :=
  ⟨regular_of_smallSubsetsBounded κ hκ, smallSubsetsBounded_of_regular κ⟩

theorem guard_initial_iff (κ : Cardinal.{u}) :
    RegularUncountableGuard κ.ord.toZFSet ↔ κ.IsRegular ∧ Cardinal.aleph0 < κ := by
  constructor
  · rintro ⟨_, hu, hr⟩
    have hu' := (hasInductiveMember_initial_iff κ).mp hu
    exact ⟨regular_of_smallSubsetsBounded κ hu'.le hr, hu'⟩
  · rintro ⟨hr, hu⟩
    exact ⟨isInitial_cardinal κ, (hasInductiveMember_initial_iff κ).mpr hu,
      smallSubsetsBounded_of_regular κ hr⟩

theorem guard_iff_exists_cardinal (K : ZFSet.{u}) :
    RegularUncountableGuard K ↔
      ∃ κ : Cardinal.{u}, K = κ.ord.toZFSet ∧ κ.IsRegular ∧ Cardinal.aleph0 < κ := by
  constructor
  · intro h
    obtain ⟨κ, rfl⟩ := (isInitial_iff_cardinal K).mp h.1
    exact ⟨κ, rfl, (guard_initial_iff κ).mp h⟩
  · rintro ⟨κ, rfl, hκ⟩
    exact (guard_initial_iff κ).mpr hκ

theorem not_guard_aleph0 : ¬ RegularUncountableGuard Cardinal.aleph0.{u}.ord.toZFSet := by
  rw [guard_initial_iff]
  simp

/-- The guard itself is satisfiable in the ordinary baseline, independently of
any compactness principle. In particular it does not hide the desired conclusion. -/
theorem guard_infinite_successor (μ : Cardinal.{u}) (hμ : Cardinal.aleph0 ≤ μ) :
    RegularUncountableGuard (Order.succ μ).ord.toZFSet := by
  apply (guard_initial_iff _).mpr
  exact ⟨Cardinal.isRegular_succ hμ, hμ.trans_lt (Order.lt_succ μ)⟩

theorem exists_guard : ∃ K : ZFSet.{u}, RegularUncountableGuard K :=
  ⟨(Order.succ Cardinal.aleph0).ord.toZFSet, guard_infinite_successor _ le_rfl⟩

end Komorebi.SetFilterCoding
