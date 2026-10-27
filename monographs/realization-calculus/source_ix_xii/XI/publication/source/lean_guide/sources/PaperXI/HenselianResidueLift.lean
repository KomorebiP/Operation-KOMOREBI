import Mathlib.RingTheory.Henselian
import Mathlib.FieldTheory.Finite.Basic
import Mathlib.RingTheory.LocalRing.ResidueField.Instances
import Mathlib.Tactic

/-! Unique multiplicative lifts of an embedded finite residue field. These are
actual Hensel roots in the given local ring, not an assumed ring section. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HenselianResidueLift
open Polynomial IsLocalRing
variable (k R : Type*) [Field k] [Fintype k] [CommRing R] [HenselianLocalRing R]
variable (e : k →+* ResidueField R)

def poly : R[X] := X ^ Fintype.card k - X

theorem poly_monic : (poly k R).Monic := by
  apply Polynomial.monic_X_pow_sub
  simpa using (Fintype.one_lt_card : 1 < Fintype.card k)

include e in
theorem card_residue_zero : (Fintype.card k : ResidueField R) = 0 := by
  rw [← map_natCast e, Nat.cast_card_eq_zero, map_zero]

include e in
theorem derivative_unit (a : R) : IsUnit ((poly k R).derivative.eval a) := by
  apply (residue_ne_zero_iff_isUnit _).mp
  simp [poly, derivative_sub, derivative_X_pow, card_residue_zero k R e]

/-- A finite residue element has a root lift of X^Q-X. -/
theorem exists_lift (x : k) : ∃ a : R, a ^ Fintype.card k = a ∧ residue R a = e x := by
  have H := ((HenselianLocalRing.TFAE R).out 1 2).mp (inferInstance : HenselianLocalRing R)
  have hr : aeval (e x) (poly k R) = 0 := by
    simp only [poly, map_sub, map_pow, aeval_X]
    rw [← map_pow, FiniteField.pow_card, sub_self]
  have hd : aeval (e x) (poly k R).derivative ≠ 0 := by
    simp [poly, derivative_sub, derivative_X_pow, card_residue_zero k R e]
  obtain ⟨a, ha, he⟩ := H (poly k R) (poly_monic k R) (e x) hr hd
  exact ⟨a, by simpa [poly, Polynomial.IsRoot, sub_eq_zero] using ha, he⟩

include e in
/-- A simple root lift is unique in its residue class, even with nilpotents in R. -/
theorem unique_lift {a b : R} (ha : a ^ Fintype.card k = a)
    (hb : b ^ Fintype.card k = b) (hab : residue R a = residue R b) : a = b := by
  apply IsLocalRing.eq_of_eval_eq_zero_of_not_isUnit_sub (f := poly k R)
  · simpa [poly, sub_eq_zero] using ha
  · simpa [poly, sub_eq_zero] using hb
  · intro h
    have hn := (residue_ne_zero_iff_isUnit _).mpr h
    exact hn (by rw [map_sub, hab, sub_self])
  · exact derivative_unit k R e a

def lift (x : k) : R := (exists_lift k R e x).choose

@[simp] theorem lift_pow (x : k) : lift k R e x ^ Fintype.card k = lift k R e x :=
  (exists_lift k R e x).choose_spec.1

@[simp] theorem residue_lift (x : k) : residue R (lift k R e x) = e x :=
  (exists_lift k R e x).choose_spec.2

theorem lift_injective : Function.Injective (lift k R e) := by
  intro x y h
  apply e.injective
  simpa only [residue_lift] using congrArg (residue R) h

@[simp] theorem lift_zero : lift k R e 0 = 0 := by
  apply unique_lift k R e (lift_pow k R e 0)
  · exact zero_pow (Fintype.card_ne_zero)
  · simp

@[simp] theorem lift_one : lift k R e 1 = 1 := by
  apply unique_lift k R e (lift_pow k R e 1)
  · exact one_pow _
  · simp

@[simp] theorem lift_mul (x y : k) : lift k R e (x*y) = lift k R e x * lift k R e y := by
  apply unique_lift k R e (lift_pow k R e (x*y))
  · rw [mul_pow, lift_pow, lift_pow]
  · simp

/-- Multiplicative section of the embedded residue field, not an additive section. -/
def sectionMonoid : k →*₀ R where
  toFun := lift k R e
  map_zero' := lift_zero k R e
  map_one' := lift_one k R e
  map_mul' := lift_mul k R e

@[simp] theorem lift_nat_pow (x : k) (n : ℕ) : lift k R e (x^n) = lift k R e x ^ n :=
  (sectionMonoid k R e).map_pow x n

theorem lift_unit {x : k} (hx : x ≠ 0) : IsUnit (lift k R e x) := by
  rw [← residue_ne_zero_iff_isUnit, residue_lift]
  exact (map_ne_zero_iff e e.injective).mpr hx

/-- Automorphisms fix precisely those lifts whose actual residue classes they fix. -/
theorem automorphism_fix_iff (σ : R ≃+* R) (x : k) :
    σ (lift k R e x) = lift k R e x ↔ residue R (σ (lift k R e x)) = e x := by
  constructor
  · intro h; rw [h, residue_lift]
  · intro h
    apply unique_lift k R e
    · rw [← map_pow, lift_pow]
    · exact lift_pow k R e x
    · rw [residue_lift]; exact h

/-- Full transport, including nontrivial residue action. -/
theorem automorphism_transport (σ : R ≃+* R) {x y : k}
    (h : residue R (σ (lift k R e x)) = e y) :
    σ (lift k R e x) = lift k R e y := by
  apply unique_lift k R e
  · rw [← map_pow, lift_pow]
  · exact lift_pow k R e y
  · rw [residue_lift]; exact h

end PaperXI.HenselianResidueLift
