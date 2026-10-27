module

public import PadicDifferenceBounds
public import Mathlib.NumberTheory.Padics.RingHoms
public import Mathlib.FieldTheory.Finite.Basic

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.UnitModes

open Mahler PadicBounds

/-- A geometric sequence has an exact h-step finite difference at every order. -/
theorem geometric_difference {R : Type*} [CommRing R] (u : R) (h s n : ℕ) :
    difference h s (fun k => u^k) n = u^n * (u^h-1)^s := by
  induction s generalizing n with
  | zero => simp
  | succ s ih =>
    rw [difference_succ, ih, ih, pow_add, pow_succ]
    ring

/-- Any proved divisibility of the one-step multiplier propagates multiplicatively. -/
theorem geometric_difference_divisibility {R : Type*} [CommRing R]
    (p u : R) (h s n k : ℕ) (hu : p^k ∣ u^h-1) :
    p^(k*s) ∣ difference h s (fun j => u^j) n := by
  rw [geometric_difference, pow_mul]
  exact dvd_mul_of_dvd_right (pow_dvd_pow_of_dvd hu s) _

/-- Linearity is applied to the actual iterated operator, including an empty mode set. -/
theorem finite_mode_formula {R ι : Type*} [CommRing R]
    (S : Finset ι) (a u : ι → R) (h s n : ℕ) :
    difference h s (fun j => ∑ i ∈ S, a i * (u i)^j) n =
      ∑ i ∈ S, a i * (u i)^n * ((u i)^h-1)^s := by
  rw [difference_sum]
  simp only [difference_mul_const, geometric_difference, mul_assoc]

variable (p : ℕ) [Fact p.Prime]

/-- Reduction to the actual residue field proves Fermat divisibility inside Z_p. -/
theorem unit_fermat_divisibility (u : ℤ_[p]ˣ) :
    (p : ℤ_[p]) ∣ (u : ℤ_[p])^(p-1)-1 := by
  have hu : IsUnit (PadicInt.toZMod (u : ℤ_[p])) :=
    u.isUnit.map (PadicInt.toZMod : ℤ_[p] →+* ZMod p)
  have hf := ZMod.pow_card_sub_one_eq_one hu.ne_zero
  have hz : PadicInt.toZMod ((u : ℤ_[p])^(p-1)-1) = 0 := by
    rw [map_sub, map_pow, map_one, hf, sub_self]
  rw [← RingHom.mem_ker, PadicInt.ker_toZMod, PadicInt.maximalIdeal_eq_span_p,
    Ideal.mem_span_singleton] at hz
  exact hz

/-- Theorem 7.4 as actual p-power divisibility, valid also for p=2 with step one. -/
theorem unit_mode_divisibility (u : ℤ_[p]ˣ) (s n : ℕ) :
    (p : ℤ_[p])^s ∣ difference (p-1) s (fun j => (u : ℤ_[p])^j) n := by
  have h := geometric_difference_divisibility (p : ℤ_[p]) (u : ℤ_[p]) (p-1) s n 1
    (by simpa using unit_fermat_divisibility p u)
  simpa using h

/-- The valuation version uses infinity at zero, so constant modes are included. -/
theorem unit_mode_valuation_gain (u : ℤ_[p]ˣ) (s n : ℕ) :
    (s : WithTop ℕ) ≤ order p (difference (p-1) s (fun j => (u : ℤ_[p])^j) n) :=
  (nat_le_order_iff p _ s).mpr (unit_mode_divisibility p u s n)

/-- All finite integral linear combinations retain the same uniform bound. -/
theorem finite_unit_modes_divisibility {ι : Type*} (S : Finset ι)
    (a : ι → ℤ_[p]) (u : ι → ℤ_[p]ˣ) (s n : ℕ) :
    (p : ℤ_[p])^s ∣ difference (p-1) s
      (fun j => ∑ i ∈ S, a i * (u i : ℤ_[p])^j) n := by
  rw [difference_sum]
  apply Finset.dvd_sum
  intro i _
  rw [difference_mul_const]
  exact dvd_mul_of_dvd_right (unit_mode_divisibility p (u i) s n) _

theorem finite_unit_modes_valuation_gain {ι : Type*} (S : Finset ι)
    (a : ι → ℤ_[p]) (u : ι → ℤ_[p]ˣ) (s n : ℕ) :
    (s : WithTop ℕ) ≤ order p (difference (p-1) s
      (fun j => ∑ i ∈ S, a i * (u i : ℤ_[p])^j) n) :=
  (nat_le_order_iff p _ s).mpr (finite_unit_modes_divisibility p S a u s n)

/-- Multiples of the Fermat step preserve the same gain; no stronger exponent is claimed. -/
theorem unit_multiple_step_divisibility (u : ℤ_[p]ˣ) (a s n : ℕ) :
    (p : ℤ_[p])^s ∣ difference (a*(p-1)) s (fun j => (u : ℤ_[p])^j) n := by
  have hstep : (p : ℤ_[p]) ∣ (u : ℤ_[p])^(a*(p-1))-1 := by
    have hu : IsUnit (PadicInt.toZMod (u : ℤ_[p])) :=
      u.isUnit.map (PadicInt.toZMod : ℤ_[p] →+* ZMod p)
    have hf := ZMod.pow_card_sub_one_eq_one hu.ne_zero
    have hz : PadicInt.toZMod ((u : ℤ_[p])^(a*(p-1))-1) = 0 := by
      rw [map_sub, map_pow, map_one, Nat.mul_comm a, pow_mul, hf, one_pow, sub_self]
    rw [← RingHom.mem_ker, PadicInt.ker_toZMod, PadicInt.maximalIdeal_eq_span_p,
      Ideal.mem_span_singleton] at hz
    exact hz
  have h := geometric_difference_divisibility (p : ℤ_[p]) (u : ℤ_[p]) (a*(p-1)) s n 1
    (by simpa using hstep)
  simpa using h

end KomorebiPaperIX.UnitModes
