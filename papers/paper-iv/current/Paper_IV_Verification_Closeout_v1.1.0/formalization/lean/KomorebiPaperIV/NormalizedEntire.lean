/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SharpGrowth
import KomorebiPaperIV.AlgebraicCompletion

namespace Komorebi.PaperIV
noncomputable section
open FormalMultilinearSeries Set Filter Metric
open scoped Topology

def entireNormalizedSection (N j : ℕ) : ℂ → ℂ :=
  ofScalarsSum (fun n => PowerSeries.coeff n (normalizedResidueSection (K := ℂ) N j))

theorem normalizedSection_coeff_norm (N j n : ℕ) :
    ‖PowerSeries.coeff n (normalizedResidueSection (K := ℂ) N j)‖ =
      (j.factorial : ℝ) / ((N * n + j).factorial : ℝ) := by
  rw [coeff_normalizedResidueSection, norm_div]
  simp

theorem normalizedSection_entire_radius {N : ℕ} (hN : 0 < N) (j : ℕ) :
    (ofScalars ℂ (fun n => PowerSeries.coeff n (normalizedResidueSection (K := ℂ) N j))).radius = ⊤ := by
  apply radius_eq_top_of_summable_norm
  intro r
  apply Summable.of_nonneg_of_le (fun n => mul_nonneg (norm_nonneg _) (pow_nonneg r.2 _))
    (fun n => ?_) ((Real.summable_pow_div_factorial (r : ℝ)).mul_left (j.factorial : ℝ))
  rw [ofScalars_norm, normalizedSection_coeff_norm]
  calc
    _ = (j.factorial : ℝ) * ((r : ℝ) ^ n / ((N * n + j).factorial : ℝ)) := by
      change ((j.factorial : ℝ) / ((N * n + j).factorial : ℝ)) * (r : ℝ) ^ n = _
      ring
    _ ≤ (j.factorial : ℝ) * ((r : ℝ) ^ n / (n.factorial : ℝ)) := by
      apply mul_le_mul_of_nonneg_left _ (by positivity)
      apply div_le_div_of_nonneg_left (pow_nonneg r.2 n) (by positivity)
      exact_mod_cast Nat.factorial_le ((Nat.le_mul_of_pos_left n hN).trans (Nat.le_add_right _ j))

theorem analyticAt_entireNormalizedSection {N : ℕ} (hN : 0 < N) (j : ℕ) (w : ℂ) :
    AnalyticAt ℂ (entireNormalizedSection N j) w := by
  apply (ofScalars ℂ (fun n => PowerSeries.coeff n (normalizedResidueSection (K := ℂ) N j))).analyticOnNhd
  rw [normalizedSection_entire_radius hN]; simp

theorem hasSum_entireNormalizedSection {N : ℕ} (hN : 0 < N) (j : ℕ) (w : ℂ) :
    HasSum (fun n => (j.factorial : ℂ) / ((N * n + j).factorial : ℂ) * w ^ n)
      (entireNormalizedSection N j w) := by
  have h := (ofScalars ℂ (fun n => PowerSeries.coeff n (normalizedResidueSection (K := ℂ) N j))).hasSum
    (x := w) (by rw [normalizedSection_entire_radius hN]; simp)
  simpa only [entireNormalizedSection, ofScalarsSum, ofScalars_apply_eq', smul_eq_mul,
    coeff_normalizedResidueSection] using h

@[simp] theorem entireNormalizedSection_zero (N j : ℕ) : entireNormalizedSection N j 0 = 1 := by
  simp [entireNormalizedSection, Nat.factorial_ne_zero]

theorem entireNormalizedSection_iteratedDeriv_zero {N : ℕ} (hN : 0 < N) (j n : ℕ) :
    iteratedDeriv n (entireNormalizedSection N j) 0 =
      (n.factorial : ℂ) * (j.factorial : ℂ) / ((N * n + j).factorial : ℂ) := by
  let p := ofScalars ℂ (fun n => PowerSeries.coeff n (normalizedResidueSection (K := ℂ) N j))
  have hp : HasFPowerSeriesAt (entireNormalizedSection N j) p 0 :=
    (p.hasFPowerSeriesOnBall (by dsimp [p]; rw [normalizedSection_entire_radius hN]; simp)).hasFPowerSeriesAt
  have he := hp.eq_formalMultilinearSeries (analyticAt_entireNormalizedSection hN j 0).hasFPowerSeriesAt
  have hc := congrArg (fun q : FormalMultilinearSeries ℂ ℂ ℂ => q.coeff n) he
  simp only [p, coeff_ofScalars] at hc
  have hn : (n.factorial : ℂ) ≠ 0 := by exact_mod_cast n.factorial_ne_zero
  have hh := ((div_eq_iff hn).mp hc.symm).trans (mul_comm _ _)
  simpa only [coeff_normalizedResidueSection, mul_div_assoc] using hh

theorem entireNormalizedSection_transfer {N j : ℕ} (hN : 0 < N) (hj : j < N)
    {ω : ℂ} (hω : IsPrimitiveRoot ω N) (z : ℂ) :
    entireNormalizedSection N j (z ^ N) * z ^ j =
      (j.factorial : ℂ) * entireTransfer N j ω 1 z := by
  have hi : Function.Injective (fun n : ℕ => N * n + j) := by
    intro a b h; exact Nat.mul_left_cancel hN (Nat.add_right_cancel h)
  have hz : ∀ n ∉ Set.range (fun m : ℕ => N * m + j),
      PowerSeries.coeff n (transferSection N j (1 : ℂ)) * z ^ n = 0 := by
    intro n hn
    have hres : n % N ≠ j := by
      intro he
      apply hn
      refine ⟨n / N, ?_⟩
      change N * (n / N) + j = n
      rw [← he, Nat.div_add_mod]
    simp [coeff_transferSection, transferSectionCoeff, hres]
  have ht := (hi.hasSum_iff hz).mpr (hasSum_entireTransfer hN hj hω (1 : ℂ) z)
  apply ((hasSum_entireNormalizedSection hN j (z ^ N)).mul_right (z ^ j)).unique
  convert ht.mul_left (j.factorial : ℂ) using 1
  funext n
  simp only [Function.comp_apply, coeff_transferSection, transferSectionCoeff, Nat.add_mod,
    Nat.mul_mod_right, zero_add, Nat.mod_eq_of_lt hj, ↓reduceIte, one_pow, one_mul]
  simp only [map_div₀, map_one, map_natCast]
  rw [← pow_mul, pow_add]
  ring

theorem entireTransfer_unit_norm_le {N : ℕ} (hN : 0 < N) (j : ℕ)
    {ω : ℂ} (hω : IsPrimitiveRoot ω N) (z : ℂ) :
    ‖entireTransfer N j ω 1 z‖ ≤ Real.exp ‖z‖ := by
  have hn : ‖ω‖ = 1 := Complex.norm_eq_one_of_pow_eq_one hω.pow_eq_one hN.ne'
  have ht (k : ℕ) : ‖((ω ^ j)⁻¹) ^ k * Complex.exp ((1 * ω ^ k) * z)‖ ≤ Real.exp ‖z‖ := by
    simp only [norm_mul, norm_pow, norm_inv, hn, one_pow, inv_one, one_mul]
    rw [Complex.norm_exp]
    apply Real.exp_le_exp.mpr
    calc
      _ ≤ ‖ω ^ k * z‖ := Complex.re_le_norm _
      _ = ‖z‖ := by simp [norm_pow, hn]
  rw [entireTransfer, norm_mul, norm_inv, Complex.norm_natCast]
  calc
    _ ≤ (N : ℝ)⁻¹ * ∑ k ∈ Finset.range N, ‖((ω ^ j)⁻¹) ^ k * Complex.exp ((1 * ω ^ k) * z)‖ :=
      mul_le_mul_of_nonneg_left (norm_sum_le _ _) (by positivity)
    _ ≤ (N : ℝ)⁻¹ * ∑ _k ∈ Finset.range N, Real.exp ‖z‖ :=
      mul_le_mul_of_nonneg_left (Finset.sum_le_sum (fun k _ => ht k)) (by positivity)
    _ = Real.exp ‖z‖ := by simp [hN.ne']

end
end Komorebi.PaperIV
