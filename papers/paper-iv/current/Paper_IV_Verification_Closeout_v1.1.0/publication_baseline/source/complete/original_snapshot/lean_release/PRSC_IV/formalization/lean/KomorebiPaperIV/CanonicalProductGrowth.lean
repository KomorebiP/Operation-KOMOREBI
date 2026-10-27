/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.FullCanonicalProduct
import Mathlib.Analysis.MeanInequalitiesPow
import Mathlib.Analysis.Complex.Polynomial.Basic

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

theorem log_one_add_le_rpow_div {x s : ℝ} (hx : 0 ≤ x) (hs : 0 < s) (hs1 : s ≤ 1) :
    Real.log (1 + x) ≤ x ^ s / s := by
  have h := Real.log_le_sub_one_of_pos (Real.rpow_pos_of_pos (by linarith : 0 < 1 + x) s)
  rw [Real.log_rpow (by linarith)] at h
  have hp := Real.rpow_add_le_add_rpow (a := 1) (b := x) zero_le_one hx hs.le hs1
  rw [Real.one_rpow] at hp
  apply (le_div_iff₀ hs).mpr
  nlinarith

theorem zeroMultiplicity_reciprocal_rpow_summable {f : ℂ → ℂ} {s : ℝ}
    (hf : ZeroPowerSummable f s) :
    Summable (fun i : ZeroMultiplicityIndex f => 1 / ‖indexedZero i‖ ^ s) := by
  apply (summable_sigma_of_nonneg (fun i : ZeroMultiplicityIndex f => by positivity)).mpr
  constructor
  · intro z
    exact (hasSum_fintype _).summable
  · simpa only [indexedZero, tsum_fintype, Finset.sum_const, Finset.card_univ,
      Fintype.card_fin, nsmul_eq_mul, mul_one_div, ZeroPowerSummable] using hf

def reciprocalPowerMass (f : ℂ → ℂ) (s : ℝ) : ℝ :=
  ∑' i : ZeroMultiplicityIndex f, 1 / ‖indexedZero i‖ ^ s

theorem reciprocalPowerMass_nonneg (f : ℂ → ℂ) (s : ℝ) : 0 ≤ reciprocalPowerMass f s :=
  tsum_nonneg (fun _ => by positivity)

/-- A genus-zero product inherits every summable reciprocal exponent below one. -/
theorem fullCanonicalProduct_growth {f : ℂ → ℂ} {s : ℝ}
    (hf : ZeroPowerSummable f 1) (hfs : ZeroPowerSummable f s)
    (hs : 0 < s) (hs1 : s ≤ 1) (w : ℂ) :
    ‖fullCanonicalProduct f w‖ ≤
      Real.exp ((reciprocalPowerMass f s / s) * ‖w‖ ^ s) := by
  have hm := zeroMultiplicity_reciprocal_rpow_summable hfs
  have hsum : Summable (fun i : ZeroMultiplicityIndex f => ‖w / indexedZero i‖ ^ s) := by
    simpa only [norm_div, Real.div_rpow (norm_nonneg _) (norm_nonneg _), mul_one_div] using
      hm.mul_left (‖w‖ ^ s)
  have he : (∑' i : ZeroMultiplicityIndex f, ‖w / indexedZero i‖ ^ s) =
      ‖w‖ ^ s * reciprocalPowerMass f s := by
    unfold reciprocalPowerMass
    rw [← tsum_mul_left]
    apply tsum_congr
    intro i
    rw [norm_div, Real.div_rpow (norm_nonneg _) (norm_nonneg _), mul_one_div]
  have ht := (continuous_norm.tendsto (fullCanonicalProduct f w)).comp
    (fullCanonicalProduct_multipliable hf w).hasProd
  apply le_of_tendsto ht
  apply Eventually.of_forall
  intro S
  calc
    ‖∏ i ∈ S, (1 - w / indexedZero i)‖ ≤ ∏ i ∈ S, Real.exp (‖w / indexedZero i‖ ^ s / s) := by
      rw [norm_prod]
      apply Finset.prod_le_prod (fun _ _ => norm_nonneg _)
      intro i _
      apply (norm_sub_le _ _).trans
      rw [norm_one]
      exact (Real.log_le_iff_le_exp (by positivity)).mp
        (log_one_add_le_rpow_div (norm_nonneg _) hs hs1)
    _ = Real.exp ((∑ i ∈ S, ‖w / indexedZero i‖ ^ s) / s) := by
      rw [← Real.exp_sum, Finset.sum_div]
    _ ≤ Real.exp ((∑' i : ZeroMultiplicityIndex f, ‖w / indexedZero i‖ ^ s) / s) := by
      apply Real.exp_le_exp.mpr
      apply div_le_div_of_nonneg_right _ hs.le
      exact hsum.sum_le_tsum S (fun _ _ => Real.rpow_nonneg (norm_nonneg _) _)
    _ = Real.exp ((reciprocalPowerMass f s / s) * ‖w‖ ^ s) := by
      rw [he]
      congr 1
      ring

/-- The reduced denominator has the explicit order-1/N upper bound. -/
theorem entireReducedDenominator_norm_le {N : ℕ} (hN : 0 < N) (w : ℂ) :
    ‖entireReducedDenominator N w‖ ≤ Real.exp (‖w‖ ^ (1 / (N : ℝ))) := by
  obtain ⟨z, rfl⟩ := IsAlgClosed.exists_pow_nat_eq w hN
  rw [← canonicalSignedDenominator_eq_reduced_power hN, norm_pow, one_div,
    Real.pow_rpow_inv_natCast (norm_nonneg z) hN.ne']
  exact norm_entireSigned_zero_le hN (canonicalPrimitiveRoot_isPrimitive hN)
    (canonicalSignedRoot_pow hN) z

/-- One fixed sublinear exponent works for every N ≥ 2, for both entire factors. -/
theorem entireReducedDenominator_and_product_growth {N : ℕ} (hN : 2 ≤ N) :
    ∃ C : ℝ, 0 ≤ C ∧ ∀ R : ℝ, 1 ≤ R → ∀ w : ℂ, ‖w‖ ≤ R →
      ‖entireReducedDenominator N w‖ ≤ Real.exp (C * R ^ (3 / 4 : ℝ)) ∧
      ‖fullCanonicalProduct (entireReducedDenominator N) w‖ ≤ Real.exp (C * R ^ (3 / 4 : ℝ)) := by
  have hN0 : 0 < N := by omega
  have hn : (2 : ℝ) ≤ N := by exact_mod_cast hN
  have hn0 : (0 : ℝ) < N := by positivity
  have he : 1 / (N : ℝ) < (3 / 4 : ℝ) := (div_lt_iff₀ hn0).mpr (by linarith)
  have hs := (entireReducedDenominator_zero_power_summable_iff hN (3 / 4)).mpr he
  let B := reciprocalPowerMass (entireReducedDenominator N) (3 / 4) / (3 / 4)
  have hB : 0 ≤ B := div_nonneg (reciprocalPowerMass_nonneg _ _) (by norm_num)
  refine ⟨1 + B, by positivity, fun R hR w hw => ?_⟩
  have hRp : 0 ≤ R ^ (3 / 4 : ℝ) := Real.rpow_nonneg (by linarith) _
  constructor
  · apply (entireReducedDenominator_norm_le hN0 w).trans
    apply Real.exp_le_exp.mpr
    calc
      ‖w‖ ^ (1 / (N : ℝ)) ≤ R ^ (1 / (N : ℝ)) :=
        Real.rpow_le_rpow (norm_nonneg _) hw (by positivity)
      _ ≤ R ^ (3 / 4 : ℝ) := Real.rpow_le_rpow_of_exponent_le hR he.le
      _ ≤ (1 + B) * R ^ (3 / 4 : ℝ) := by nlinarith
  · apply (fullCanonicalProduct_growth (entireReducedDenominator_reciprocal_zeros_summable hN)
      hs (by norm_num) (by norm_num) w).trans
    apply Real.exp_le_exp.mpr
    change B * ‖w‖ ^ (3 / 4 : ℝ) ≤ _
    calc
      _ ≤ B * R ^ (3 / 4 : ℝ) := mul_le_mul_of_nonneg_left
        (Real.rpow_le_rpow (norm_nonneg _) hw (by norm_num)) hB
      _ ≤ (1 + B) * R ^ (3 / 4 : ℝ) := by nlinarith

end
end Komorebi.PaperIV
