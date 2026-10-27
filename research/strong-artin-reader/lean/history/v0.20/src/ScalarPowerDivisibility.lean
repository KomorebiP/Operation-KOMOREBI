import PowerDivisibility

/-!
# Multiplicative power-divisibility over the coefficient ring

The nonlinear polynomial remainder argument needs the elementary fact that
products add filtration depths.  This module keeps that calculation separate
from the expression syntax.
-/

namespace Komorebi.StrongArtin.ScalarPowerDivisibility

open Komorebi.StrongArtin.PowerDivisibility

variable {R : Type*} [CommRing R]

/-- Multiplying a divisible scalar by an arbitrary scalar preserves its depth. -/
theorem powDivisible_mul_right {pi : R} {n : ℕ} {a : R}
    (ha : PowDivisible pi n a) (b : R) :
    PowDivisible pi n (a * b) := by
  obtain ⟨a₀, rfl⟩ := ha
  refine ⟨a₀ * b, ?_⟩
  simp [smul_eq_mul, mul_assoc]

/-- Multiplying on the left by an arbitrary scalar preserves depth. -/
theorem powDivisible_mul_left {pi : R} {n : ℕ} (a : R) {b : R}
    (hb : PowDivisible pi n b) :
    PowDivisible pi n (a * b) := by
  obtain ⟨b₀, rfl⟩ := hb
  refine ⟨a * b₀, ?_⟩
  simp only [smul_eq_mul]
  ring

/-- Products add filtration depths. -/
theorem powDivisible_mul {pi : R} {m n : ℕ} {a b : R}
    (ha : PowDivisible pi m a) (hb : PowDivisible pi n b) :
    PowDivisible pi (m + n) (a * b) := by
  obtain ⟨a₀, rfl⟩ := ha
  obtain ⟨b₀, rfl⟩ := hb
  refine ⟨a₀ * b₀, ?_⟩
  simp [smul_eq_mul, pow_add]
  ring

/-- Evaluation at one coordinate preserves divisibility of a function vector. -/
theorem powDivisible_apply {ι : Type*} {pi : R} {n : ℕ} {x : ι → R}
    (hx : PowDivisible pi n x) (i : ι) :
    PowDivisible pi n (x i) := by
  obtain ⟨x₀, rfl⟩ := hx
  exact ⟨x₀ i, by simp [smul_eq_mul]⟩

end Komorebi.StrongArtin.ScalarPowerDivisibility

#print axioms Komorebi.StrongArtin.ScalarPowerDivisibility.powDivisible_mul
#print axioms Komorebi.StrongArtin.ScalarPowerDivisibility.powDivisible_apply
