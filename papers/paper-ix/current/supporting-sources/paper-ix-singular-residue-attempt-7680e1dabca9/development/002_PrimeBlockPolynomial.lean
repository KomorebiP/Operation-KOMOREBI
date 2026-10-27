module
public import CyclotomicFiltration
public import Mathlib.FieldTheory.Finite.Basic
public import Mathlib.RingTheory.Polynomial.Pochhammer
public import Mathlib.Tactic
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.PrimeBlockPolynomial
open Polynomial CyclotomicFiltration
/-- Literal falling-factorial polynomial. -/
def falling (n : ℕ) : Polynomial ℤ :=
  ∏ i ∈ Finset.range n, (X-C (i:ℤ))
/-- Literal product in any commutative ring. -/
def fallingAt {R : Type*} [CommRing R] (x : R) (n : ℕ) : R :=
  ∏ i ∈ Finset.range n, (x-(i:R))
theorem falling_eval {R : Type*} [CommRing R] (x : R) (n : ℕ) :
    (falling n).eval₂ (Int.castRingHom R) x = fallingAt x n := by
  change (eval₂RingHom (Int.castRingHom R) x) (falling n) = fallingAt x n
  simp only [falling, fallingAt, map_prod]
  simp
/-- Product over the actual prime field, not assumed Fermat factorization. -/
theorem prime_field_falling (p : ℕ) (hp : p.Prime) :
    (falling p).map (Int.castRingHom (ZMod p)) = X^p-X := by
  classical
  let : Fact p.Prime := ⟨hp⟩
  have hm : (X^p-X : Polynomial (ZMod p)).Monic :=
    monic_X_pow_sub (by simpa using hp.one_lt)
  have hr : (X^p-X : Polynomial (ZMod p)).roots = Finset.univ.val := by
    simpa using FiniteField.roots_X_pow_card_sub_X (K:=ZMod p)
  have hprod := prod_multiset_X_sub_C_of_monic_of_roots_card_eq hm (by
    rw [hr]
    simp [FiniteField.X_pow_card_sub_X_natDegree_eq (ZMod p) hp.one_lt])
  rw [hr] at hprod
  have hbij : (∏ i ∈ Finset.range p, (X-C (i:ZMod p))) =
      ∏ a : ZMod p, (X-C a) := by
    apply Finset.prod_bij (fun (i : ℕ) (_ : i∈Finset.range p) => (i:ZMod p))
    · intros; exact Finset.mem_univ _
    · intro i hi j hj hij
      have hh := congrArg ZMod.val hij
      simpa [ZMod.val_natCast_of_lt (Finset.mem_range.mp hi),
        ZMod.val_natCast_of_lt (Finset.mem_range.mp hj)] using hh
    · intro a _
      exact ⟨a.val, Finset.mem_range.mpr (ZMod.val_lt a), by simp⟩
    · intros; rfl
  rw [falling, Polynomial.map_prod]
  simp only [Polynomial.map_sub, Polynomial.map_X, Polynomial.map_C,
    Int.coe_castRingHom, Int.cast_natCast]
  rw [hbij]
  simpa using hprod
/-- An integral polynomial certificate for the deviation from Fermat's polynomial. -/
theorem falling_defect_divisible (p : ℕ) (hp : p.Prime) :
    C (p:ℤ) ∣ falling p - (X^p-X) := by
  rw [C_dvd_iff_dvd_coeff]
  intro d
  have hmap : (falling p - (X^p-X)).map (Int.castRingHom (ZMod p))=0 := by
    simp [prime_field_falling p hp]
  have hc := congrArg (coeff · d) hmap
  simp only [coeff_map, Int.coe_castRingHom, coeff_zero] at hc
  exact (ZMod.intCast_zmod_eq_zero_iff_dvd _ _).mp hc
/-- Each consecutive p-block belongs to the explicit augmentation ideal. -/
theorem block_mem (p : ℕ) (hp : p.Prime) {R : Type*} [CommRing R] (x : R) (b : ℕ) :
    (∏ i ∈ Finset.range p, (x-((p*b+i):R))) ∈ torsionIdeal p (x^(p-1)) := by
  classical
  let I := torsionIdeal p (x^(p-1))
  let π := Ideal.Quotient.mk I
  have hp0 : π (p:R)=0 := Ideal.Quotient.eq_zero_iff_mem.mpr (prime_mem p _)
  have hx0 : π (x^p-x)=0 := by
    have h : x^p-x=x*(x^(p-1)-1) := by
      rw [mul_sub, ←pow_succ', Nat.sub_add_cancel hp.one_le, mul_one]
    rw [h, map_mul, Ideal.Quotient.eq_zero_iff_mem.mpr (augmentation_mem p _), mul_zero]
  obtain ⟨q,hq⟩ := falling_defect_divisible p hp
  let ev := eval₂RingHom (Int.castRingHom R) x
  have he := congrArg ev hq
  have hC : ev (C (p:ℤ))=(p:R) := by simp [ev]
  have hX : ev X=x := rfl
  have hF : ev (falling p)=fallingAt x p := falling_eval x p
  simp only [map_sub, map_mul, map_pow, hC, hX, hF] at he
  have hfall : π (fallingAt x p)=0 := by
    have h := congrArg π he
    simp only [map_sub, map_mul, hp0, hx0, zero_mul, sub_zero] at h
    exact h
  apply Ideal.Quotient.eq_zero_iff_mem.mp
  rw [map_prod]
  change (∏ i ∈ Finset.range p, π (x-((p*b+i):R)))=0
  convert hfall using 1
  rw [fallingAt, map_prod]
  apply Finset.prod_congr rfl
  intro i _
  simp [map_sub, map_add, map_mul, hp0]
end KomorebiPaperIX.PrimeBlockPolynomial
