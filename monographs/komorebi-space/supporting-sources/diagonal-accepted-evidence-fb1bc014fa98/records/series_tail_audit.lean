import Mathlib.Analysis.PSeries
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Topology.Algebra.InfiniteSum.Real
import Mathlib.Tactic

set_option autoImplicit false
noncomputable section

open Filter
open scoped Topology

namespace KomorebiSpace.DiagonalRegularization

lemma series_tail_sum_range_le_telescope (f g : ℕ → ℝ)
    (hfg : ∀ j, f j ≤ g j - g (j + 1)) (n : ℕ) :
    ∑ j ∈ Finset.range n, f j ≤ g 0 - g n := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Finset.sum_range_succ]
    calc
      (∑ j ∈ Finset.range n, f j) + f n ≤
          (g 0 - g n) + (g n - g (n + 1)) := add_le_add ih (hfg n)
      _ = g 0 - g (n + 1) := by ring

lemma series_tail_telescope_le_sum_range (f g : ℕ → ℝ)
    (hfg : ∀ j, g j - g (j + 1) ≤ f j) (n : ℕ) :
    g 0 - g n ≤ ∑ j ∈ Finset.range n, f j := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [Finset.sum_range_succ]
    calc
      g 0 - g (n + 1) = (g 0 - g n) + (g n - g (n + 1)) := by ring
      _ ≤ (∑ j ∈ Finset.range n, f j) + f n := add_le_add ih (hfg n)

lemma series_tail_sq_upper_step (x : ℝ) (hx : 0 < x) :
    1 / (x + 1)^2 ≤ 1 / x - 1 / (x + 1) := by
  have hxp : 0 < x + 1 := by linarith
  have heq : 1 / x - 1 / (x + 1) - 1 / (x + 1)^2 =
      1 / (x * (x + 1)^2) := by
    field_simp [ne_of_gt hx, ne_of_gt hxp]; ring
  have hnonneg : 0 ≤ 1 / (x * (x + 1)^2) := by positivity
  linarith

lemma series_tail_sq_lower_step (x : ℝ) (hx : 0 < x) :
    1 / x - 1 / (x + 1) ≤ 1 / x^2 := by
  have hxp : 0 < x + 1 := by linarith
  have heq : 1 / x^2 - (1 / x - 1 / (x + 1)) =
      1 / (x^2 * (x + 1)) := by
    field_simp [ne_of_gt hx, ne_of_gt hxp]; ring
  have hnonneg : 0 ≤ 1 / (x^2 * (x + 1)) := by positivity
  linarith

lemma series_tail_fourth_upper_step (x : ℝ) (hx : 0 < x) :
    1 / (x + 1)^4 ≤ 1 / (3 * x^3) - 1 / (3 * (x + 1)^3) := by
  have hxp : 0 < x + 1 := by linarith
  have heq : 1 / (3 * x^3) - 1 / (3 * (x + 1)^3) - 1 / (x + 1)^4 =
      (6*x^2 + 4*x + 1) / (3*x^3*(x + 1)^4) := by
    field_simp [ne_of_gt hx, ne_of_gt hxp]; ring
  have hnonneg : 0 ≤ (6*x^2 + 4*x + 1) / (3*x^3*(x + 1)^4) := by positivity
  linarith

lemma series_tail_sq_partial_upper (K n : ℕ) (hK : 1 ≤ K) :
    ∑ j ∈ Finset.range n, 1 / ((K : ℝ) + j + 1)^2 ≤ 1 / (K : ℝ) := by
  have hKpos : 0 < (K : ℝ) := by exact_mod_cast (lt_of_lt_of_le Nat.zero_lt_one hK)
  have hstep : ∀ j : ℕ, 1 / ((K : ℝ) + j + 1)^2 ≤
      1 / ((K : ℝ) + j) - 1 / ((K : ℝ) + (j + 1 : ℕ)) := by
    intro j
    simpa only [Nat.cast_add, Nat.cast_one, add_assoc] using
      series_tail_sq_upper_step ((K : ℝ) + j) (by positivity)
  have h := series_tail_sum_range_le_telescope
    (fun j => 1 / ((K : ℝ) + j + 1)^2)
    (fun j => 1 / ((K : ℝ) + j)) hstep n
  simp only [Nat.cast_zero, add_zero] at h
  have hnonneg : 0 ≤ 1 / ((K : ℝ) + n) := by positivity
  linarith

lemma series_tail_fourth_partial_upper (K n : ℕ) (hK : 1 ≤ K) :
    ∑ j ∈ Finset.range n, 1 / ((K : ℝ) + j + 1)^4 ≤ 1 / (3 * (K : ℝ)^3) := by
  have hKpos : 0 < (K : ℝ) := by exact_mod_cast (lt_of_lt_of_le Nat.zero_lt_one hK)
  have hstep : ∀ j : ℕ, 1 / ((K : ℝ) + j + 1)^4 ≤
      1 / (3 * ((K : ℝ) + j)^3) - 1 / (3 * ((K : ℝ) + (j + 1 : ℕ))^3) := by
    intro j
    simpa only [Nat.cast_add, Nat.cast_one, add_assoc] using
      series_tail_fourth_upper_step ((K : ℝ) + j) (by positivity)
  have h := series_tail_sum_range_le_telescope
    (fun j => 1 / ((K : ℝ) + j + 1)^4)
    (fun j => 1 / (3 * ((K : ℝ) + j)^3)) hstep n
  simp only [Nat.cast_zero, add_zero] at h
  have hnonneg : 0 ≤ 1 / (3 * ((K : ℝ) + n)^3) := by positivity
  linarith

lemma series_tail_sq_partial_lower (K n : ℕ) :
    1 / ((K : ℝ) + 1) - 1 / ((K : ℝ) + n + 1) ≤
      ∑ j ∈ Finset.range n, 1 / ((K : ℝ) + j + 1)^2 := by
  have hstep : ∀ j : ℕ, 1 / ((K : ℝ) + j + 1) -
      1 / ((K : ℝ) + (j + 1 : ℕ) + 1) ≤ 1 / ((K : ℝ) + j + 1)^2 := by
    intro j
    simpa only [Nat.cast_add, Nat.cast_one, add_assoc] using
      series_tail_sq_lower_step ((K : ℝ) + j + 1) (by positivity)
  have h := series_tail_telescope_le_sum_range
    (fun j => 1 / ((K : ℝ) + j + 1)^2)
    (fun j => 1 / ((K : ℝ) + j + 1)) hstep n
  simpa only [Nat.cast_zero, add_zero] using h

lemma series_tail_sq_upper (K : ℕ) (hK : 1 ≤ K) :
    (∑' j : ℕ, 1 / ((K : ℝ) + j + 1)^2) ≤ 1 / (K : ℝ) := by
  exact Real.tsum_le_of_sum_range_le (fun j => by positivity)
    (fun n => series_tail_sq_partial_upper K n hK)

lemma series_tail_fourth_upper (K : ℕ) (hK : 1 ≤ K) :
    (∑' j : ℕ, 1 / ((K : ℝ) + j + 1)^4) ≤ 1 / (3 * (K : ℝ)^3) := by
  exact Real.tsum_le_of_sum_range_le (fun j => by positivity)
    (fun n => series_tail_fourth_partial_upper K n hK)

lemma series_tail_sq_lower (K : ℕ)
    (hsum : Summable (fun j : ℕ => 1 / ((K : ℝ) + j + 1)^2)) :
    1 / ((K : ℝ) + 1) ≤ ∑' j : ℕ, 1 / ((K : ℝ) + j + 1)^2 := by
  have hinv : Tendsto (fun n : ℕ => 1 / ((K : ℝ) + n + 1)) atTop (𝓝 0) := by
    simpa only [Nat.cast_add, add_comm, add_left_comm, add_assoc] using
      (tendsto_add_atTop_iff_nat K).2 (tendsto_one_div_add_atTop_nhds_zero_nat (𝕜 := ℝ))
  have hleft : Tendsto (fun n : ℕ => 1 / ((K : ℝ) + 1) -
      1 / ((K : ℝ) + n + 1)) atTop (𝓝 (1 / ((K : ℝ) + 1))) := by
    simpa only [sub_zero] using (tendsto_const_nhds (x := 1 / ((K : ℝ) + 1))).sub hinv
  exact le_of_tendsto_of_tendsto' hleft hsum.hasSum.tendsto_sum_nat
    (fun n => series_tail_sq_partial_lower K n)

end KomorebiSpace.DiagonalRegularization

#print axioms KomorebiSpace.DiagonalRegularization.series_tail_sq_upper
#print axioms KomorebiSpace.DiagonalRegularization.series_tail_fourth_upper
#print axioms KomorebiSpace.DiagonalRegularization.series_tail_sq_lower
