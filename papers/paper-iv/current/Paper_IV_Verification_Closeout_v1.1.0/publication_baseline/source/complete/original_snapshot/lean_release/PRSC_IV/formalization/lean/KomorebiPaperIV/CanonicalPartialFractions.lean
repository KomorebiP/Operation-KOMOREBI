/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.HadamardIdentification
import Mathlib.Analysis.Calculus.LogDerivUniformlyOn
import Mathlib.Topology.Algebra.InfiniteSum.TsumUniformlyOn

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

def zeroPartialFraction (f : ℂ → ℂ) (i : ZeroMultiplicityIndex f) (w : ℂ) : ℂ :=
  1 / (indexedZero i - w)

theorem zeroPartialFraction_uniform_majorant {f : ℂ → ℂ}
    (hf : ZeroPowerSummable f 1) (hf0 : f 0 ≠ 0) {B : ℝ} (hB : 0 ≤ B) :
    ∀ᶠ i : ZeroMultiplicityIndex f in cofinite, ∀ w : ℂ, ‖w‖ ≤ B →
      ‖zeroPartialFraction f i w‖ ≤ 2 / ‖indexedZero i‖ := by
  have ht := (zeroMultiplicity_reciprocal_summable hf).tendsto_cofinite_zero
  have hC : 0 < 2 * (B + 1) := by positivity
  filter_upwards [ht.eventually (gt_mem_nhds (one_div_pos.mpr hC))] with i hi
  intro w hw
  have ha : 0 < ‖indexedZero i‖ := norm_pos_iff.mpr (indexedZero_ne_zero hf0 i)
  have hlarge : 2 * (B + 1) < ‖indexedZero i‖ := by
    simpa only [one_mul] using (div_lt_div_iff₀ ha hC).mp hi
  have htri := norm_sub_norm_le (indexedZero i) w
  have hd : 0 < ‖indexedZero i - w‖ := by linarith
  simp only [zeroPartialFraction, norm_div, norm_one]
  apply (div_le_div_iff₀ hd ha).mpr
  nlinarith

theorem zeroPartialFraction_norm_summable {f : ℂ → ℂ}
    (hf : ZeroPowerSummable f 1) (hf0 : f 0 ≠ 0) (w : ℂ) :
    Summable (fun i : ZeroMultiplicityIndex f => ‖zeroPartialFraction f i w‖) := by
  have hm := (zeroMultiplicity_reciprocal_summable hf).mul_left 2
  apply hm.of_norm_bounded_eventually
  filter_upwards [zeroPartialFraction_uniform_majorant hf hf0 (norm_nonneg w)] with i hi
  simpa only [norm_norm, mul_one_div] using hi w le_rfl

/-- Compact-uniform convergence of the unregularized partial fractions. -/
theorem zeroPartialFraction_uniform_on_compact {f : ℂ → ℂ}
    (hf : ZeroPowerSummable f 1) (hf0 : f 0 ≠ 0) {K : Set ℂ} (hK : IsCompact K) :
    HasSumUniformlyOn (zeroPartialFraction f) (fun w => ∑' i, zeroPartialFraction f i w) K := by
  obtain ⟨B, hB⟩ := hK.isBounded.exists_norm_le
  have hb : 0 ≤ max 0 B := le_max_left _ _
  apply HasSumUniformlyOn.of_norm_le_summable_eventually ((zeroMultiplicity_reciprocal_summable hf).mul_left 2)
  filter_upwards [zeroPartialFraction_uniform_majorant hf hf0 hb] with i hi
  intro w hw
  simpa only [mul_one_div] using hi w ((hB w hw).trans (le_max_right _ _))

theorem logDeriv_linear_factor {a w : ℂ} (ha : a ≠ 0) (hw : w ≠ a) :
    logDeriv (fun z : ℂ => 1 - z / a) w = -(1 / (a - w)) := by
  rw [logDeriv_apply]
  erw [((hasDerivAt_const w (1 : ℂ)).sub ((hasDerivAt_id w).div_const a)).deriv]
  have hwa : a - w ≠ 0 := sub_ne_zero.mpr hw.symm
  field_simp
  ring

theorem fullCanonicalProduct_logDeriv {f : ℂ → ℂ}
    (hf : ZeroPowerSummable f 1) (hf0 : f 0 ≠ 0) {w : ℂ}
    (hw : ∀ i : ZeroMultiplicityIndex f, w ≠ indexedZero i) :
    -logDeriv (fullCanonicalProduct f) w = ∑' i, zeroPartialFraction f i w := by
  have hn : ∀ i : ZeroMultiplicityIndex f, 1 - w / indexedZero i ≠ 0 := by
    intro i
    rw [sub_ne_zero]
    intro he
    exact hw i ((div_eq_one_iff_eq (indexedZero_ne_zero hf0 i)).mp he.symm)
  have he : (fun i : ZeroMultiplicityIndex f => logDeriv (fun z : ℂ => 1 - z / indexedZero i) w) =
      (fun i => -zeroPartialFraction f i w) := by
    funext i
    exact logDeriv_linear_factor (indexedZero_ne_zero hf0 i) (hw i)
  have hs : Summable (fun i : ZeroMultiplicityIndex f => logDeriv (fun z : ℂ => 1 - z / indexedZero i) w) := by
    rw [he]
    exact (zeroPartialFraction_norm_summable hf hf0 w).of_norm.neg
  have h := logDeriv_tprod_eq_tsum isOpen_univ (mem_univ w) hn
    (fun _ => by fun_prop) hs (fullCanonicalProduct_locally_uniform hf).multipliableLocallyUniformlyOn
    (fullCanonicalProduct_ne_zero hf hf0 hw)
  change logDeriv (fullCanonicalProduct f) w = _ at h
  rw [he, tsum_neg] at h
  linear_combination -h

theorem entireReducedDenominator_partialFractions {N : ℕ} (hN : 2 ≤ N)
    {w : ℂ} (hw : entireReducedDenominator N w ≠ 0) :
    -logDeriv (entireReducedDenominator N) w =
      ∑' i : ZeroMultiplicityIndex (entireReducedDenominator N), 1 / (indexedZero i - w) := by
  have hf0 : entireReducedDenominator N 0 ≠ 0 := by rw [entireReducedDenominator_zero]; exact one_ne_zero
  have hneq : ∀ i : ZeroMultiplicityIndex (entireReducedDenominator N), w ≠ indexedZero i := by
    intro i he
    apply hw
    rw [he]
    exact i.1.property
  have h := fullCanonicalProduct_logDeriv (entireReducedDenominator_reciprocal_zeros_summable hN) hf0 hneq
  simpa only [← entireReducedDenominator_eq_fullCanonicalProduct hN, zeroPartialFraction] using h

theorem zeroPartialFraction_locally_uniform {f : ℂ → ℂ}
    (hf : ZeroPowerSummable f 1) (hf0 : f 0 ≠ 0) :
    HasSumLocallyUniformlyOn (zeroPartialFraction f) (fun w => ∑' i, zeroPartialFraction f i w) univ := by
  apply hasSumLocallyUniformlyOn_of_forall_compact isOpen_univ
  intro K _ hK
  exact zeroPartialFraction_uniform_on_compact hf hf0 hK

/-- The manuscript's tangent as an actual meromorphic function. -/
def analyticTransferTangent (N : ℕ) (z : ℂ) : ℂ :=
  -logDeriv (canonicalSignedDenominator N) z

theorem analyticTransferTangent_eq_reduced_logDeriv {N : ℕ} (hN : 0 < N) (z : ℂ) :
    analyticTransferTangent N z =
      (N : ℂ) * z ^ (N - 1) * (-logDeriv (entireReducedDenominator N) (z ^ N)) := by
  have he : canonicalSignedDenominator N = entireReducedDenominator N ∘ (fun w : ℂ => w ^ N) :=
    funext (canonicalSignedDenominator_eq_reduced_power hN)
  rw [analyticTransferTangent, he, logDeriv_comp
    (analyticAt_entireReducedDenominator hN _).differentiableAt (by fun_prop)]
  rw [(hasDerivAt_pow N z).deriv]
  ring

/-- Corollary 12.7: the full, unregularized Mittag-Leffler identity. -/
theorem analyticTransferTangent_mittagLeffler {N : ℕ} (hN : 2 ≤ N)
    {z : ℂ} (hz : canonicalSignedDenominator N z ≠ 0) :
    analyticTransferTangent N z = (N : ℂ) * z ^ (N - 1) *
      ∑' i : ZeroMultiplicityIndex (entireReducedDenominator N), 1 / (indexedZero i - z ^ N) := by
  have hw : entireReducedDenominator N (z ^ N) ≠ 0 := by
    rwa [← canonicalSignedDenominator_eq_reduced_power (by omega)]
  rw [analyticTransferTangent_eq_reduced_logDeriv (by omega), entireReducedDenominator_partialFractions hN hw]

theorem analyticTransferTangent_mittagLeffler_absolute {N : ℕ} (hN : 2 ≤ N) (z : ℂ) :
    Summable (fun i : ZeroMultiplicityIndex (entireReducedDenominator N) =>
      ‖(1 : ℂ) / (indexedZero i - z ^ N)‖) :=
  zeroPartialFraction_norm_summable (entireReducedDenominator_reciprocal_zeros_summable hN)
    (by rw [entireReducedDenominator_zero]; exact one_ne_zero) _

/-- Uniform convergence is asserted for the summed fractions. The formula for
the tangent is restricted to nonpoles in the preceding theorem. -/
theorem analyticTransferTangent_mittagLeffler_locally_uniform {N : ℕ} (hN : 2 ≤ N) :
    HasSumLocallyUniformlyOn
      (fun (i : ZeroMultiplicityIndex (entireReducedDenominator N)) z => 1 / (indexedZero i - z ^ N))
      (fun z => ∑' i : ZeroMultiplicityIndex (entireReducedDenominator N), 1 / (indexedZero i - z ^ N))
      univ := by
  have h := zeroPartialFraction_locally_uniform (entireReducedDenominator_reciprocal_zeros_summable hN)
    (by rw [entireReducedDenominator_zero]; exact one_ne_zero)
  exact h.comp (fun z : ℂ => z ^ N) (mapsTo_univ _ _) (by fun_prop : ContinuousOn (fun z : ℂ => z ^ N) univ)

end
end Komorebi.PaperIV
