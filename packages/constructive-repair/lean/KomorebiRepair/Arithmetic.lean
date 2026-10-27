import Mathlib.RingTheory.Coprime.Basic
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.NormNum

/-! # Quadratic digit repair, with explicit arithmetic hypotheses
This is a finite Hensel digit step, not a proof of all nonlinear or infinite lifts.
-/
namespace KomorebiRepair.Arithmetic

/-- A Bezout certificate constructs a solution of the new linear congruence. -/
theorem linear_digit_exists (p A c : ℤ) (h : IsCoprime A p) :
    ∃ t : ℤ, p ∣ c + A * t := by
  obtain ⟨s, b, hsb⟩ := h
  refine ⟨-s * c, b * c, ?_⟩
  linear_combination -c * hsb

/-- The exact quadratic expansion proves that a correct digit raises precision. -/
theorem quadratic_digit_correction (p m x a c t : ℤ)
    (hbase : x ^ 2 - a = m * c)
    (hdigit : p ∣ c + 2 * x * t) (hscale : p ∣ m) :
    m * p ∣ (x + m * t) ^ 2 - a := by
  obtain ⟨d, hd⟩ := hdigit
  obtain ⟨s, hs⟩ := hscale
  refine ⟨d + s * t ^ 2, ?_⟩
  calc
    (x + m * t) ^ 2 - a = (x ^ 2 - a) + m * (2 * x * t) + m ^ 2 * t ^ 2 := by ring
    _ = m * (c + 2 * x * t) + m ^ 2 * t ^ 2 := by rw [hbase]; ring
    _ = m * p * (d + s * t ^ 2) := by rw [hd, hs]; ring

/-- A unit derivative modulo `p`, expressed by Bezout, gives an actual next digit. -/
theorem quadratic_hensel_step (p x a : ℤ) (k : ℕ) (hk : 1 ≤ k)
    (hbase : p ^ k ∣ x ^ 2 - a) (hunit : IsCoprime (2 * x) p) :
    ∃ t : ℤ, p ^ (k + 1) ∣ (x + p ^ k * t) ^ 2 - a := by
  obtain ⟨c, hc⟩ := hbase
  obtain ⟨t, ht⟩ := linear_digit_exists p (2 * x) c hunit
  refine ⟨t, ?_⟩
  rw [pow_succ]
  exact quadratic_digit_correction p (p ^ k) x a c t hc ht
    (by simpa using pow_dvd_pow p hk)

theorem hensel_seven_trace :
    (7 : ℤ) ∣ 3 ^ 2 - 2 ∧
    (7 : ℤ) ^ 2 ∣ 10 ^ 2 - 2 ∧
    (7 : ℤ) ^ 3 ∣ 108 ^ 2 - 2 ∧
    (7 : ℤ) ^ 4 ∣ 2166 ^ 2 - 2 ∧
    (7 : ℤ) ^ 5 ∣ 4567 ^ 2 - 2 ∧
    (7 : ℤ) ^ 6 ∣ 38181 ^ 2 - 2 ∧
    (7 : ℤ) ^ 7 ∣ 155830 ^ 2 - 2 := by norm_num

theorem singular_mod_four_impossible : ¬ ∃ x : ZMod 4, x ^ 2 = 2 := by decide

theorem singular_derivative_can_still_lift (k : ℕ) :
    (2 : ℤ) ^ k ∣ (1 : ℤ) ^ 2 - 1 := by simp

end KomorebiRepair.Arithmetic
