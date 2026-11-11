import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

/-! Exact squared-coefficient sums; no angular Parseval bridge is assumed. -/

namespace SmithEnergy

noncomputable def laneEnergy (ρ : ℝ) (N j : ℕ) : ℝ :=
  ∑' m : ℕ, 4 * ρ ^ (2 * (j + m * N))

noncomputable def impedanceCoefficientEnergy (ρ : ℝ) (N j : ℕ) : ℝ :=
  if j = 0 then 1 + laneEnergy ρ N N else laneEnergy ρ N j

theorem lane_hasSum {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    {N : ℕ} (hN : 0 < N) (j : ℕ) :
    HasSum (fun m : ℕ => 4 * ρ ^ (2 * (j + m * N)))
      (4 * ρ ^ (2 * j) / (1 - ρ ^ (2 * N))) := by
  have hnorm : ‖ρ‖ < 1 := by simpa [Real.norm_eq_abs, abs_of_nonneg hρ0] using hρ1
  have hexp : 2 * N ≠ 0 := by omega
  have hn : ‖ρ ^ (2 * N)‖ < 1 := by
    rw [norm_pow]
    exact pow_lt_one₀ (norm_nonneg ρ) hnorm hexp
  have hs := (hasSum_geometric_of_norm_lt_one hn).mul_left (4 * ρ ^ (2 * j))
  have hf : (fun m : ℕ => 4 * ρ ^ (2 * (j + m * N))) =
      (fun m : ℕ => (4 * ρ ^ (2 * j)) * (ρ ^ (2 * N)) ^ m) := by
    funext m
    have hm : 2 * (m * N) = (2 * N) * m := by ring
    rw [Nat.mul_add, hm, pow_add, pow_mul]
    ring
  rw [hf]
  simpa only [div_eq_mul_inv] using hs

theorem lane_closed {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    {N : ℕ} (hN : 0 < N) (j : ℕ) :
    laneEnergy ρ N j = 4 * ρ ^ (2 * j) / (1 - ρ ^ (2 * N)) :=
  (lane_hasSum hρ0 hρ1 hN j).tsum_eq

theorem coefficient_energy_zero {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    {N : ℕ} (hN : 0 < N) :
    impedanceCoefficientEnergy ρ N 0 = 1 + 4 * ρ ^ (2 * N) / (1 - ρ ^ (2 * N)) := by
  simp [impedanceCoefficientEnergy, lane_closed hρ0 hρ1 hN]

theorem coefficient_energy_nonzero {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    {N j : ℕ} (hN : 0 < N) (hj : j ≠ 0) :
    impedanceCoefficientEnergy ρ N j = 4 * ρ ^ (2 * j) / (1 - ρ ^ (2 * N)) := by
  simp [impedanceCoefficientEnergy, hj, lane_closed hρ0 hρ1 hN]

end SmithEnergy
