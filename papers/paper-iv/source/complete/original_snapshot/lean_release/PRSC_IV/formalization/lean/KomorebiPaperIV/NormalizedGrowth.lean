/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.NormalizedEntire
import KomorebiPaperIV.WeightedGrowthSummability

namespace Komorebi.PaperIV
noncomputable section
open Set Filter Real
open scoped Topology

theorem entireNormalizedSection_norm_le {N : ℕ} (hN : 0 < N) (j : ℕ) (w : ℂ) :
    ‖entireNormalizedSection N j w‖ ≤ (j.factorial : ℝ) * exp (‖w‖ ^ (1 / (N : ℝ))) := by
  let t := ‖w‖ ^ (1 / (N : ℝ))
  have ht : 0 ≤ t := rpow_nonneg (norm_nonneg _) _
  have htN : t ^ N = ‖w‖ := by
    dsimp [t]; rw [one_div, rpow_inv_natCast_pow (norm_nonneg _) hN.ne']
  have hi : Function.Injective (fun n : ℕ => N * n) := fun a b h => Nat.mul_left_cancel hN h
  have hs := (Real.summable_pow_div_factorial t).comp_injective hi
  have hle := (hasSum_entireNormalizedSection hN j w).norm_le_of_bounded
    (hs.hasSum.mul_left (j.factorial : ℝ)) (fun n => ?_)
  · apply hle.trans
    apply mul_le_mul_of_nonneg_left _ (by positivity)
    calc
      _ ≤ ∑' n : ℕ, t ^ n / (n.factorial : ℝ) := tsum_comp_le_tsum_of_inj
        (Real.summable_pow_div_factorial t) (fun n => by positivity) hi
      _ = exp t := by simpa only [Real.exp_eq_exp_ℝ] using (NormedSpace.expSeries_div_hasSum_exp t).tsum_eq
  · simp only [norm_mul, norm_div, norm_pow, Complex.norm_natCast, Function.comp_apply]
    rw [← htN, pow_mul]
    calc
      _ = (j.factorial : ℝ) * (t ^ (N * n) / ((N * n + j).factorial : ℝ)) := by rw [pow_mul]; ring
      _ ≤ (j.factorial : ℝ) * (t ^ (N * n) / ((N * n).factorial : ℝ)) := by
        apply mul_le_mul_of_nonneg_left _ (by positivity)
        apply div_le_div_of_nonneg_left (pow_nonneg ht _) (by positivity)
        exact_mod_cast Nat.factorial_le (Nat.le_add_right (N * n) j)
      _ = _ := by rw [pow_mul]

def normalizedSectionGrowthConstant (j : ℕ) : ℝ := 1 + log (j.factorial : ℝ)

theorem normalizedSectionGrowthConstant_pos (j : ℕ) : 0 < normalizedSectionGrowthConstant j := by
  have hj : (1 : ℝ) ≤ j.factorial := by exact_mod_cast Nat.factorial_pos j
  have := log_nonneg hj
  unfold normalizedSectionGrowthConstant
  linarith

theorem entireNormalizedSection_disk_growth {N : ℕ} (hN : 0 < N) (j : ℕ)
    (R : ℝ) (hR : 1 ≤ R) (w : ℂ) (hw : ‖w‖ ≤ R) :
    ‖entireNormalizedSection N j w‖ ≤
      exp (normalizedSectionGrowthConstant j * R ^ (1 / (N : ℝ))) := by
  have hj : (1 : ℝ) ≤ j.factorial := by exact_mod_cast Nat.factorial_pos j
  have hp : 0 ≤ 1 / (N : ℝ) := by positivity
  have hpow : 1 ≤ R ^ (1 / (N : ℝ)) := one_le_rpow hR hp
  apply (entireNormalizedSection_norm_le hN j w).trans
  calc
    _ ≤ (j.factorial : ℝ) * exp (R ^ (1 / (N : ℝ))) := mul_le_mul_of_nonneg_left
      (exp_le_exp.mpr (rpow_le_rpow (norm_nonneg _) hw hp)) (by positivity)
    _ = exp (log (j.factorial : ℝ) + R ^ (1 / (N : ℝ))) := by rw [exp_add, exp_log (by positivity)]
    _ ≤ _ := by apply exp_le_exp.mpr; unfold normalizedSectionGrowthConstant; nlinarith [log_nonneg hj]

theorem entireNormalizedSection_zeroPowerSummable {N : ℕ} (hN : 0 < N) (j : ℕ)
    {q : ℝ} (hq : 1 / (N : ℝ) < q) : ZeroPowerSummable (entireNormalizedSection N j) q :=
  entire_growth_zeroPowerSummable
    (fun w => (analyticAt_entireNormalizedSection hN j w).differentiableAt)
    (entireNormalizedSection_zero N j) (normalizedSectionGrowthConstant_pos j).le (by positivity)
    hq (entireNormalizedSection_disk_growth hN j)

end
end Komorebi.PaperIV
