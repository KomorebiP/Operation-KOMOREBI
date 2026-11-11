import Mathlib.Analysis.Complex.Basic
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

/-! Algebraic sensitivity and the abstract equal-mass minimax principle. -/

open scoped BigOperators

namespace SmithSampling

theorem symmetric_weight_algebra (x y : ℝ)
    (hm : (1 - x) ^ 2 + y ^ 2 ≠ 0) (hp : (1 + x) ^ 2 + y ^ 2 ≠ 0) :
    1 / ((1 - x) ^ 2 + y ^ 2) + 1 / ((1 + x) ^ 2 + y ^ 2) =
      (2 * (1 + x ^ 2 + y ^ 2)) /
        (1 - 2 * (x ^ 2 - y ^ 2) + (x ^ 2 + y ^ 2) ^ 2) := by
  have hd : 1 - 2 * (x ^ 2 - y ^ 2) + (x ^ 2 + y ^ 2) ^ 2 =
      ((1 - x) ^ 2 + y ^ 2) * ((1 + x) ^ 2 + y ^ 2) := by ring
  rw [hd]
  field_simp [hm, hp]; ring

/-- The actual angular sensitivity is the displayed rational Poisson shape. -/
theorem angular_weight (ρ θ : ℝ) (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) :
    1 / ((1 - ρ * Real.cos θ) ^ 2 + (ρ * Real.sin θ) ^ 2) +
      1 / ((1 + ρ * Real.cos θ) ^ 2 + (ρ * Real.sin θ) ^ 2) =
      (2 * (1 + ρ ^ 2)) / (1 - 2 * ρ ^ 2 * Real.cos (2 * θ) + ρ ^ 4) := by
  have hminus : (1 - ρ * Real.cos θ) ^ 2 + (ρ * Real.sin θ) ^ 2 ≠ 0 := by
    have hp : 0 ≤ ρ * (1 - Real.cos θ) :=
      mul_nonneg hρ0 (sub_nonneg.mpr (Real.cos_le_one θ))
    have hleft : 0 < 1 - ρ * Real.cos θ := by nlinarith
    have hs := sq_pos_of_pos hleft
    have hy := sq_nonneg (ρ * Real.sin θ)
    nlinarith
  have hplus : (1 + ρ * Real.cos θ) ^ 2 + (ρ * Real.sin θ) ^ 2 ≠ 0 := by
    have hp : 0 ≤ ρ * (1 + Real.cos θ) :=
      mul_nonneg hρ0 (by linarith [Real.neg_one_le_cos θ])
    have hleft : 0 < 1 + ρ * Real.cos θ := by nlinarith
    have hs := sq_pos_of_pos hleft
    have hy := sq_nonneg (ρ * Real.sin θ)
    nlinarith
  rw [symmetric_weight_algebra _ _ hminus hplus]
  have hsum : (ρ * Real.cos θ) ^ 2 + (ρ * Real.sin θ) ^ 2 = ρ ^ 2 := by
    calc
      _ = ρ ^ 2 * (Real.cos θ ^ 2 + Real.sin θ ^ 2) := by ring
      _ = _ := by rw [Real.cos_sq_add_sin_sq]; ring
  have hdiff : (ρ * Real.cos θ) ^ 2 - (ρ * Real.sin θ) ^ 2 =
      ρ ^ 2 * Real.cos (2 * θ) := by
    rw [Real.cos_two_mul']
    ring
  have hnum : 1 + (ρ * Real.cos θ) ^ 2 + (ρ * Real.sin θ) ^ 2 = 1 + ρ ^ 2 := by
    nlinarith [hsum]
  have hden : 1 - 2 * ((ρ * Real.cos θ) ^ 2 - (ρ * Real.sin θ) ^ 2) +
      ((ρ * Real.cos θ) ^ 2 + (ρ * Real.sin θ) ^ 2) ^ 2 =
      1 - 2 * ρ ^ 2 * Real.cos (2 * θ) + ρ ^ 4 := by
    rw [hsum, hdiff]
    ring
  rw [hnum, hden]

/-- Every upper bound on N interval masses dominates their average. -/
theorem average_le_upper_bound {N : ℕ} (hN : 0 < N) (mass : Fin N → ℝ) (B : ℝ)
    (hB : ∀ i, mass i ≤ B) : (∑ i, mass i) / N ≤ B := by
  have hn : (0 : ℝ) < N := by exact_mod_cast hN
  apply (div_le_iff₀ hn).2
  calc
    (∑ i, mass i) ≤ ∑ _i : Fin N, B := Finset.sum_le_sum (fun i _ => hB i)
    _ = B * N := by simp [mul_comm]

/-- Equal masses attain the lower bound for the maximum interval mass. -/
theorem equal_mass_minimax {N : ℕ} (hN : 0 < N)
    (mass ideal : Fin N → ℝ) (total B : ℝ)
    (hTotal : ∑ i, mass i = total)
    (hIdeal : ∀ i, ideal i = total / N)
    (hB : ∀ i, mass i ≤ B) : ∀ i, ideal i ≤ B := by
  intro i
  rw [hIdeal i, ← hTotal]
  exact average_le_upper_bound hN mass B hB

end SmithSampling
