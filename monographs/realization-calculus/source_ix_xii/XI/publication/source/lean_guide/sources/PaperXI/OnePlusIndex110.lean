import Mathlib.GroupTheory.Index
import Mathlib.RingTheory.Ideal.Basic
import Mathlib.Logic.Equiv.Defs
import Mathlib.Tactic.NoncommRing

/-! Exact multiplicative/additive coset comparison. The named unit subgroup K
must really consist of all units 1+x for x in L. This does not pretend that
an arbitrary full lattice contained in a radical automatically is a group. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.OnePlusIndex110

variable {R : Type*} [Ring R]

def congruence (I : Ideal R) (K : Subgroup Rˣ) : Subgroup K where
  carrier := {g | ((g : Rˣ) : R) - 1 ∈ I}
  one_mem' := by simp
  mul_mem' := by
    intro a b ha hb
    change (((a : Rˣ) : R) * ((b : Rˣ) : R)) - 1 ∈ I
    have he : (((a : Rˣ) : R) * ((b : Rˣ) : R)) - 1 =
        ((a : Rˣ) : R) * (((b : Rˣ) : R) - 1) + (((a : Rˣ) : R) - 1) := by noncomm_ring
    rw [he]
    exact I.add_mem (I.mul_mem_left _ hb) ha
  inv_mem' := by
    intro a ha
    change (((a : Rˣ)⁻¹ : Rˣ) : R) - 1 ∈ I
    have he : (((a : Rˣ)⁻¹ : Rˣ) : R) - 1 =
        -((((a : Rˣ)⁻¹ : Rˣ) : R) * (((a : Rˣ) : R) - 1)) := by
      rw [mul_sub, Units.inv_mul, mul_one]
      abel
    rw [he]
    exact I.neg_mem (I.mul_mem_left _ ha)

def offsetEquiv (L : AddSubgroup R) (K : Subgroup Rˣ)
    (hK : ∀ g : K, ((g : Rˣ) : R) - 1 ∈ L)
    (hL : ∀ x : L, ∃ g : K, ((g : Rˣ) : R) = 1 + (x : R)) : K ≃ L :=
  Equiv.ofBijective (fun g => ⟨((g : Rˣ) : R) - 1, hK g⟩) (by
    constructor
    · intro a b hab
      apply Subtype.ext
      apply Units.ext
      have he := congrArg (fun x : L => (x : R)) hab
      exact sub_left_injective he
    · intro x
      obtain ⟨g, hg⟩ := hL x
      refine ⟨g, Subtype.ext ?_⟩
      change ((g : Rˣ) : R) - 1 = (x : R)
      rw [hg]
      abel)

theorem inv_mul_sub_one_mem_iff (I : Ideal R) (a b : Rˣ) :
    (((a⁻¹ * b : Rˣ) : R) - 1 ∈ I) ↔ ((b : R) - (a : R) ∈ I) := by
  have hleft : ((a⁻¹ * b : Rˣ) : R) - 1 = (↑a⁻¹ : R) * ((b : R) - (a : R)) := by
    rw [mul_sub, Units.inv_mul]
    rfl
  have hright : (b : R) - (a : R) = (a : R) * (((a⁻¹ * b : Rˣ) : R) - 1) := by
    rw [mul_sub, Units.val_mul, ← mul_assoc, Units.mul_inv, one_mul, mul_one]
  constructor
  · intro h
    rw [hright]
    exact I.mul_mem_left _ h
  · intro h
    rw [hleft]
    exact I.mul_mem_left _ h

def cosetEquiv (I : Ideal R) (L : AddSubgroup R) (K : Subgroup Rˣ)
    (hK : ∀ g : K, ((g : Rˣ) : R) - 1 ∈ L)
    (hL : ∀ x : L, ∃ g : K, ((g : Rˣ) : R) = 1 + (x : R)) :
    (K ⧸ congruence I K) ≃ (L ⧸ I.toAddSubgroup.addSubgroupOf L) :=
  Quotient.congr (offsetEquiv L K hK hL) (by
    intro a b
    rw [QuotientGroup.leftRel_apply, QuotientAddGroup.leftRel_apply]
    change (((((a : Rˣ)⁻¹) * (b : Rˣ)) : R) - 1 ∈ I) ↔
      (-(((a : Rˣ) : R) - 1) + (((b : Rˣ) : R) - 1) ∈ I)
    have he : -(((a : Rˣ) : R) - 1) + (((b : Rˣ) : R) - 1) =
        ((b : Rˣ) : R) - ((a : Rˣ) : R) := by abel
    rw [he]
    exact inv_mul_sub_one_mem_iff I (a : Rˣ) (b : Rˣ))

theorem index_eq_additive_relIndex (I : Ideal R) (L : AddSubgroup R) (K : Subgroup Rˣ)
    (hK : ∀ g : K, ((g : Rˣ) : R) - 1 ∈ L)
    (hL : ∀ x : L, ∃ g : K, ((g : Rˣ) : R) = 1 + (x : R)) :
    (congruence I K).index = I.toAddSubgroup.relIndex L :=
  Nat.card_congr (cosetEquiv I L K hK hL)

end PaperXI.OnePlusIndex110
