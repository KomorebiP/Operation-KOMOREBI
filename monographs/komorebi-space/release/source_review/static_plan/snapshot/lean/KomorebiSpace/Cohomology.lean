import Mathlib.GroupTheory.QuotientGroup.Basic
import Mathlib.Tactic.Abel

set_option autoImplicit false

/-!
# The additive obstruction sector

C¹ --δ₁--> C² --δ₂--> C³ with δ₂δ₁ = 0.
No assertion is made that arbitrary categorical square defects automatically
form such a complex. An application must supply and verify this structure.
-/
universe u v w z
namespace KomorebiSpace

structure ObstructionComplex (A : Type u) (B : Type v) (C : Type w)
    [AddCommGroup A] [AddCommGroup B] [AddCommGroup C] where
  d₁ : A →+ B
  d₂ : B →+ C
  square_zero : ∀ a, d₂ (d₁ a) = 0

namespace ObstructionComplex
variable {A : Type u} {B : Type v} {C : Type w}
variable [AddCommGroup A] [AddCommGroup B] [AddCommGroup C]

abbrev Cycles (K : ObstructionComplex A B C) := K.d₂.ker

def boundaryMap (K : ObstructionComplex A B C) : A →+ K.Cycles where
  toFun := fun a => ⟨K.d₁ a, K.square_zero a⟩
  map_zero' := by apply Subtype.ext; exact map_zero K.d₁
  map_add' := by intro a b; apply Subtype.ext; exact map_add K.d₁ a b

abbrev H2 (K : ObstructionComplex A B C) := K.Cycles ⧸ K.boundaryMap.range

def obstructionClass (K : ObstructionComplex A B C) (ω : K.Cycles) : K.H2 :=
  (ω : K.Cycles ⧸ K.boundaryMap.range)

theorem class_zero_iff (K : ObstructionComplex A B C) (ω : K.Cycles) :
    K.obstructionClass ω = 0 ↔ ∃ a, K.d₁ a = ω.val := by
  change (ω : K.Cycles ⧸ K.boundaryMap.range) = 0 ↔ _
  rw [QuotientAddGroup.eq_zero_iff]
  constructor
  · rintro ⟨a, ha⟩
    exact ⟨a, congrArg Subtype.val ha⟩
  · rintro ⟨a, ha⟩
    exact ⟨a, Subtype.ext ha⟩

/-- This is standard cohomological flattening, not a general descent theorem. -/
theorem flatten_iff (K : ObstructionComplex A B C) (ω : K.Cycles) :
    K.obstructionClass ω = 0 ↔ ∃ a, ω.val - K.d₁ a = 0 := by
  rw [K.class_zero_iff]
  constructor
  · rintro ⟨a, ha⟩; exact ⟨a, sub_eq_zero.mpr ha.symm⟩
  · rintro ⟨a, ha⟩; exact ⟨a, (sub_eq_zero.mp ha).symm⟩

def correct (K : ObstructionComplex A B C) (ω : K.Cycles) (a : A) : K.Cycles :=
  ⟨ω.val - K.d₁ a, by
    change K.d₂ (ω.val - K.d₁ a) = 0
    rw [map_sub, K.square_zero, show K.d₂ ω.val = 0 from ω.property, sub_self]⟩

/-- Gauge correction does not change the obstruction class. -/
theorem correction_invariant (K : ObstructionComplex A B C) (ω : K.Cycles) (a : A) :
    K.obstructionClass (K.correct ω a) = K.obstructionClass ω := by
  have hc : K.correct ω a = ω - K.boundaryMap a := rfl
  have hz : (K.boundaryMap a : K.Cycles ⧸ K.boundaryMap.range) = 0 :=
    (QuotientAddGroup.eq_zero_iff _).2 ⟨a, rfl⟩
  change (K.correct ω a : K.Cycles ⧸ K.boundaryMap.range) = _
  rw [hc, QuotientAddGroup.mk_sub, hz, sub_zero]
  rfl

/-- A globally given primary coboundary never yields a nonzero H² class. -/
theorem primary_defect_class_zero (K : ObstructionComplex A B C) (a : A) :
    K.obstructionClass (K.boundaryMap a) = 0 :=
  (K.class_zero_iff _).2 ⟨a, rfl⟩

theorem obstruction_certificate (K : ObstructionComplex A B C)
    {D : Type z} [AddCommGroup D] (L : B →+ D)
    (hL : ∀ a, L (K.d₁ a) = 0) (ω : K.Cycles)
    (hw : L ω.val ≠ 0) : K.obstructionClass ω ≠ 0 := by
  intro h
  rcases (K.class_zero_iff ω).1 h with ⟨a, ha⟩
  apply hw
  rw [← ha]
  exact hL a
end ObstructionComplex

namespace Differential
variable {A : Type u} [AddCommGroup A]

/-- Anticommuting differentials use the unsigned total differential d+e. -/
theorem anticommuting_sum_square_zero (d e : A →+ A)
    (hd : ∀ x, d (d x) = 0) (he : ∀ x, e (e x) = 0)
    (hde : ∀ x, d (e x) + e (d x) = 0) (x : A) :
    (d + e) ((d + e) x) = 0 := by
  change d (d x + e x) + e (d x + e x) = 0
  rw [map_add, map_add, hd, he]
  simpa only [zero_add, add_zero] using hde x
end Differential
end KomorebiSpace
