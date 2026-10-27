import PaperIRelease.AlgebraSupport
import PaperIRelease.AlgebraTransfer
import PaperIRelease.PacketAggregation
import Mathlib.Order.Antisymmetrization
import Mathlib.RingTheory.TwoSidedIdeal.Operations
import Mathlib.Order.ConditionallyCompleteLattice.Basic
import Mathlib.RingTheory.Ideal.Operations

set_option autoImplicit false
set_option linter.unusedSectionVars false
set_option maxHeartbeats 3000000
noncomputable section

namespace Komorebi.PaperIRelease
open Komorebi.Foundation

universe u v w
variable {K : Type u} [Field K]
variable {X : Type v} [AddCommGroup X] [Module K X]
variable {I : Type w} [Fintype I] [DecidableEq I] [Preorder I]

abbrev preorderSupportAlgebra (P : LinearProjectorFamily K X I) :=
  supportSubalgebra P (· ≤ ·) (fun _ => le_rfl) (fun _ _ _ => le_trans)

theorem strictSupport_mul_left (P : LinearProjectorFamily K X I)
    {S T : Module.End K X} (hS : OperatorSupported P (· ≤ ·) S)
    (hT : OperatorSupported P (· < ·) T) :
    OperatorSupported P (· < ·) (S*T) := by
  apply (operatorSupported_iff_ambient P _ _).mpr
  intro b a hab
  change transferBlock P P (S.comp T) b a = 0
  rw [transferBlock_comp_end]
  apply Finset.sum_eq_zero
  intro c _
  by_cases hac : a < c
  · have hcb : ¬ c ≤ b := fun h => hab (lt_of_lt_of_le hac h)
    rw [(operatorSupported_iff_ambient P _ S).mp hS b c hcb]
    simp
  · rw [(operatorSupported_iff_ambient P _ T).mp hT c a hac]
    simp

theorem strictSupport_mul_right (P : LinearProjectorFamily K X I)
    {S T : Module.End K X} (hS : OperatorSupported P (· < ·) S)
    (hT : OperatorSupported P (· ≤ ·) T) :
    OperatorSupported P (· < ·) (S*T) := by
  apply (operatorSupported_iff_ambient P _ _).mpr
  intro b a hab
  change transferBlock P P (S.comp T) b a = 0
  rw [transferBlock_comp_end]
  apply Finset.sum_eq_zero
  intro c _
  by_cases hac : a ≤ c
  · have hcb : ¬ c < b := fun h => hab (lt_of_le_of_lt hac h)
    rw [(operatorSupported_iff_ambient P _ S).mp hS b c hcb]
    simp
  · rw [(operatorSupported_iff_ambient P _ T).mp hT c a hac]
    simp

/-- The strict-class blocks form a genuine two-sided ideal of the preorder support algebra. -/
def strictSupportIdeal (P : LinearProjectorFamily K X I) :
    TwoSidedIdeal (preorderSupportAlgebra P) :=
  TwoSidedIdeal.mk' {T | OperatorSupported P (· < ·) T.1}
    ((supportSubmodule P (· < ·)).zero_mem)
    (fun hS hT => (supportSubmodule P (· < ·)).add_mem hS hT)
    (fun hT => (supportSubmodule P (· < ·)).neg_mem hT)
    (fun {S _T} hT => strictSupport_mul_left P S.property hT)
    (fun {_S T} hS => strictSupport_mul_right P hS T.property)

@[simp] theorem mem_strictSupportIdeal (P : LinearProjectorFamily K X I)
    (T : preorderSupportAlgebra P) :
    T ∈ strictSupportIdeal P ↔ OperatorSupported P (· < ·) T.1 :=
  TwoSidedIdeal.mem_mk' _ _ _ _ _ _ T

/-- Inside the preorder support algebra, strict support means zero on every equivalence class. -/
theorem strictSupport_iff_same_class_zero (P : LinearProjectorFamily K X I)
    (T : preorderSupportAlgebra P) :
    OperatorSupported P (· < ·) T.1 ↔
      ∀ a b, AntisymmRel (· ≤ ·) a b → transferBlock P P T.1 b a = 0 := by
  constructor
  · intro h a b hab
    exact (operatorSupported_iff_ambient P _ T.1).mp h b a
      (fun hlt => (not_le_of_gt hlt) hab.2)
  · intro h
    apply (operatorSupported_iff_ambient P _ T.1).mpr
    intro b a hab
    by_cases hle : a ≤ b
    · exact h a b ⟨hle, by by_contra hback; exact hab (lt_of_le_not_ge hle hback)⟩
    · exact (operatorSupported_iff_ambient P _ T.1).mp T.property b a hle

/-- A strict path records its exact number of strict steps. -/
def StrictPath : ℕ → I → I → Prop
  | 0, a, b => a = b
  | n+1, a, b => ∃ c, StrictPath n a c ∧ c < b

private def strictPredecessors (b : I) : Finset I := by
  classical
  exact Finset.univ.filter (fun a => a < b)

private theorem predecessors_strict_mono {a b : I} (hab : a < b) :
    (strictPredecessors a).card < (strictPredecessors b).card := by
  classical
  apply Finset.card_lt_card
  apply Finset.ssubset_iff_subset_ne.mpr
  refine ⟨?_, ?_⟩
  · intro c hc
    simp only [strictPredecessors, Finset.mem_filter, Finset.mem_univ, true_and] at hc ⊢
    exact lt_trans hc hab
  · intro heq
    have ha : a ∈ strictPredecessors b := by simp [strictPredecessors, hab]
    rw [← heq] at ha
    simp [strictPredecessors] at ha

private theorem strictPath_height {n : ℕ} {a b : I} (h : StrictPath n a b) :
    (strictPredecessors a).card + n ≤ (strictPredecessors b).card := by
  induction n generalizing b with
  | zero =>
    change a = b at h
    subst b
    simp
  | succ n ih =>
    obtain ⟨c, hac, hcb⟩ := h
    have hc := ih hac
    have hb := predecessors_strict_mono hcb
    omega

private theorem strictPath_length_bound {n : ℕ} {a b : I} (h : StrictPath n a b) :
    n ≤ Fintype.card I := by
  have hn := strictPath_height h
  have hb : (strictPredecessors b).card ≤ Fintype.card I := by
    exact (Finset.card_le_card (Finset.subset_univ _)).trans_eq (Finset.card_univ)
  omega

/-- Maximum number of strict steps, with value zero for the empty preorder. -/
def maximalStrictSteps (I : Type w) [Fintype I] [DecidableEq I] [Preorder I] : ℕ :=
  sSup {n | ∃ a b : I, StrictPath n a b}

private theorem strictPath_lengths_bdd :
    BddAbove {n | ∃ a b : I, StrictPath n a b} := by
  refine ⟨Fintype.card I, ?_⟩
  rintro n ⟨a, b, h⟩
  exact strictPath_length_bound h

theorem strictPath_le_maximal {n : ℕ} {a b : I} (h : StrictPath n a b) :
    n ≤ maximalStrictSteps I :=
  le_csSup strictPath_lengths_bdd ⟨a,b,h⟩

theorem maximalStrictSteps_attained [Nonempty I] :
    ∃ a b : I, StrictPath (maximalStrictSteps I) a b := by
  apply Nat.sSup_mem _ strictPath_lengths_bdd
  obtain ⟨a⟩ := ‹Nonempty I›
  exact ⟨0, a, a, rfl⟩

theorem no_strictPath_after_maximal (a b : I) :
    ¬ StrictPath (maximalStrictSteps I + 1) a b := by
  intro h
  have hh := strictPath_le_maximal h
  omega

/-- A nonzero block of a product of strict operators forces a strict path of the same length. -/
theorem nonzero_word_block_strictPath (P : LinearProjectorFamily K X I)
    (ts : List (Module.End K X))
    (hstrict : ∀ T ∈ ts, OperatorSupported P (· < ·) T) (b a : I)
    (hne : transferBlock P P (operatorWord ts) b a ≠ 0) :
    StrictPath ts.length a b := by
  induction ts generalizing b a with
  | nil =>
    change a = b
    by_contra hab
    apply hne
    ext x
    exact P.orthogonal (Ne.symm hab) x
  | cons T ts ih =>
    have hsum : (∑ c, (transferBlock P P T b c).comp
        (transferBlock P P (operatorWord ts) c a)) ≠ 0 := by
      simpa only [operatorWord, transferBlock_comp_end] using hne
    obtain ⟨c, _, hc⟩ := Finset.exists_ne_zero_of_sum_ne_zero hsum
    have hTc : transferBlock P P T b c ≠ 0 := by
      intro h
      apply hc
      simp [h]
    have hts : transferBlock P P (operatorWord ts) c a ≠ 0 := by
      intro h
      apply hc
      simp [h]
    have hcb : c < b := by
      by_contra h
      exact hTc ((operatorSupported_iff_ambient P _ T).mp (hstrict T (by simp)) b c h)
    exact ⟨c, ih (fun S hS => hstrict S (by simp [hS])) c a hts, hcb⟩

/-- Every product of more factors than the maximal strict chain length is zero. -/
theorem strict_word_zero (P : LinearProjectorFamily K X I)
    (ts : List (Module.End K X))
    (hlen : ts.length = maximalStrictSteps I + 1)
    (hstrict : ∀ T ∈ ts, OperatorSupported P (· < ·) T) :
    operatorWord ts = 0 := by
  have hblocks : ∀ b a, transferBlock P P (operatorWord ts) b a = 0 := by
    intro b a
    by_contra h
    have hp := nonzero_word_block_strictPath P ts hstrict b a h
    rw [hlen] at hp
    exact no_strictPath_after_maximal a b hp
  ext x
  rw [← transferBlock_reconstruction P P (operatorWord ts) x]
  change (∑ b, ∑ a, transferBlock P P (operatorWord ts) b a x) = 0
  simp [hblocks]

/-- The ideal power is the span of all products of the declared number of factors. -/
def strictSupportPower (P : LinearProjectorFamily K X I) (n : ℕ) :
    Submodule K (Module.End K X) :=
  Submodule.span K {T | ∃ ts : List (Module.End K X), ts.length = n ∧
    (∀ S ∈ ts, OperatorSupported P (· < ·) S) ∧ T = operatorWord ts}

/-- Literal ideal-power nilpotence with the maximal-chain exponent. -/
theorem strictSupportPower_eq_bot (P : LinearProjectorFamily K X I) :
    strictSupportPower P (maximalStrictSteps I + 1) = ⊥ := by
  apply le_antisymm _ bot_le
  apply Submodule.span_le.mpr
  rintro T ⟨ts, hlen, hstrict, rfl⟩
  exact strict_word_zero P ts hlen hstrict

private theorem strict_mul_power_mem (P : LinearProjectorFamily K X I)
    {S T : Module.End K X} {n : ℕ} (hS : OperatorSupported P (· < ·) S)
    (hT : T ∈ strictSupportPower P n) : S*T ∈ strictSupportPower P (n+1) := by
  induction hT using Submodule.span_induction with
  | mem T hT =>
    obtain ⟨ts, hlen, hstrict, rfl⟩ := hT
    apply Submodule.subset_span
    refine ⟨S :: ts, by simp [hlen], ?_, rfl⟩
    intro U hU
    rcases List.mem_cons.mp hU with rfl | hU
    · exact hS
    · exact hstrict U hU
  | zero => simp
  | add T U _ _ hT hU =>
    rw [mul_add]
    exact (strictSupportPower P (n+1)).add_mem hT hU
  | smul c T _ hT =>
    rw [mul_smul_comm]
    exact (strictSupportPower P (n+1)).smul_mem c hT

/-- Standard ideal powers are controlled by the explicit span-of-products construction. -/
theorem strictIdeal_power_mem (P : LinearProjectorFamily K X I) (n : ℕ)
    {T : preorderSupportAlgebra P}
    (hT : T ∈ (strictSupportIdeal P).asIdeal ^ (n+1)) :
    T.1 ∈ strictSupportPower P (n+1) := by
  induction n generalizing T with
  | zero =>
    have hs : OperatorSupported P (· < ·) T.1 := by
      simpa only [Nat.zero_add, Submodule.pow_one, TwoSidedIdeal.mem_asIdeal,
        mem_strictSupportIdeal] using hT
    apply Submodule.subset_span
    exact ⟨[T.1], rfl, by simpa using hs, by ext x; rfl⟩
  | succ n ih =>
    rw [Submodule.pow_succ' _ (by omega)] at hT
    refine Submodule.smul_induction_on
      (p := fun V : preorderSupportAlgebra P => V.1 ∈ strictSupportPower P (n+1+1)) hT ?_ ?_
    · intro S hS U hU
      have hs : OperatorSupported P (· < ·) S.1 := by
        simpa only [TwoSidedIdeal.mem_asIdeal, mem_strictSupportIdeal] using hS
      exact strict_mul_power_mem P hs (ih hU)
    · intro U V hU hV
      exact (strictSupportPower P (n+1+1)).add_mem hU hV

/-- Nilpotency in Mathlib's ordinary ideal-power operation, with the exact chain-height bound. -/
theorem strictSupportIdeal_pow_eq_bot (P : LinearProjectorFamily K X I) :
    (strictSupportIdeal P).asIdeal ^ (maximalStrictSteps I + 1) = ⊥ := by
  apply le_antisymm _ bot_le
  intro T hT
  have h := strictIdeal_power_mem P (maximalStrictSteps I) hT
  rw [strictSupportPower_eq_bot] at h
  change T.1 = 0 at h
  exact Subtype.ext h

end Komorebi.PaperIRelease
