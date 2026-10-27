/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.IndicatorGeometry
import Mathlib.Topology.Order.LiminfLimsup

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

/-- Radii at which the two conjugate leading phases are both one. -/
def alignedRadii (b : ℝ) (n : ℕ) : ℝ :=
  if b = 0 then (n : ℝ) else (2 * Real.pi / |b|) * n

theorem alignedRadii_tendsto (b : ℝ) : Tendsto (alignedRadii b) atTop atTop := by
  change Tendsto (fun n : ℕ => if b = 0 then (n : ℝ) else (2 * Real.pi / |b|) * n) atTop atTop
  by_cases hb : b = 0
  · simp only [hb, ite_true]
    exact tendsto_natCast_atTop_atTop
  · simp only [hb, ite_false]
    have hC : 0 < 2 * Real.pi / |b| := div_pos (mul_pos (by norm_num) Real.pi_pos) (abs_pos.mpr hb)
    exact (tendsto_natCast_atTop_atTop (R := ℝ)).const_mul_atTop hC

theorem alignedRadii_phase (b : ℝ) (n : ℕ) :
    Complex.exp (((b * alignedRadii b n : ℝ) : ℂ) * Complex.I) = 1 := by
  by_cases hb : b = 0
  · simp [alignedRadii, hb]
  · by_cases hp : 0 < b
    · have he : (((b * alignedRadii b n : ℝ) : ℂ) * Complex.I) =
          (n : ℤ) * (2 * (Real.pi : ℂ) * Complex.I) := by
        simp only [alignedRadii, ite_eq_right hb, abs_of_pos hp]
        push_cast
        field_simp [show (b : ℂ) ≠ 0 by exact_mod_cast hb]
      rw [he, Complex.exp_int_mul_two_pi_mul_I]
    · have hn : b < 0 := lt_of_le_of_ne (le_of_not_gt hp) hb
      have he : (((b * alignedRadii b n : ℝ) : ℂ) * Complex.I) =
          (-(n : ℤ)) * (2 * (Real.pi : ℂ) * Complex.I) := by
        simp only [alignedRadii, ite_eq_right hb, abs_of_neg hn]
        push_cast
        field_simp [show (b : ℂ) ≠ 0 by exact_mod_cast hb]
      rw [he]
      simpa only [Int.cast_neg] using Complex.exp_int_mul_two_pi_mul_I (-(n : ℤ))

/-- Equal maximal real parts on the unit circle have synchronized phases. -/
theorem alignedRadii_equal_projection {a b : ℂ} (ha : ‖a‖ = 1) (hb : ‖b‖ = 1)
    (he : b.re = a.re) (n : ℕ) :
    Complex.exp ((b - (a.re : ℂ)) * (alignedRadii a.im n : ℂ)) = 1 := by
  have hphase : Complex.exp (((a.im * alignedRadii a.im n : ℝ) : ℂ) * Complex.I) = 1 :=
    alignedRadii_phase a.im n
  rcases unit_complex_same_real hb ha he with h | h
  · rw [h]
    have hx : (a - (a.re : ℂ)) * (alignedRadii a.im n : ℂ) =
        (((a.im * alignedRadii a.im n : ℝ) : ℂ) * Complex.I) := by
      apply Complex.ext <;> simp
    rwa [hx]
  · rw [h]
    have hx : (star a - (a.re : ℂ)) * (alignedRadii a.im n : ℂ) =
        -(((a.im * alignedRadii a.im n : ℝ) : ℂ) * Complex.I) := by
      apply Complex.ext <;> simp
    rw [hx, Complex.exp_neg, hphase, inv_one]

/-- Every term below the maximal real part decays along the aligned radii. -/
theorem alignedRadii_lower_projection {a b : ℂ} (he : b.re < a.re) :
    Tendsto (fun n => Complex.exp ((b - (a.re : ℂ)) * (alignedRadii a.im n : ℂ))) atTop (𝓝 0) := by
  apply tendsto_zero_iff_norm_tendsto_zero.mpr
  have ht := Real.tendsto_exp_neg_atTop_nhds_zero.comp
    ((alignedRadii_tendsto a.im).const_mul_atTop (sub_pos.mpr he))
  convert! ht using 1
  funext n
  rw [Complex.norm_exp]
  congr 1
  simp only [Complex.mul_re, Complex.sub_re, Complex.ofReal_re, Complex.sub_im, Complex.ofReal_im, mul_zero, sub_zero]
  ring

/-- For a finite sum with unit exponents, a positive number of aligned leading
terms survive. This proves a lower indicator sequence even on tie directions. -/
theorem finite_unit_exponential_aligned_limit {s : Finset ℕ} {a : ℕ → ℂ}
    {k : ℕ} (hk : k ∈ s) (ha : ∀ i ∈ s, ‖a i‖ = 1)
    (hmax : ∀ i ∈ s, (a i).re ≤ (a k).re) :
    Tendsto (fun n => ∑ i ∈ s, Complex.exp ((a i - ((a k).re : ℂ)) * (alignedRadii (a k).im n : ℂ)))
      atTop (𝓝 (((s.filter (fun i => (a i).re = (a k).re)).card : ℕ) : ℂ)) := by
  have ht : ∀ i ∈ s, Tendsto
      (fun n => Complex.exp ((a i - ((a k).re : ℂ)) * (alignedRadii (a k).im n : ℂ)))
      atTop (𝓝 (if (a i).re = (a k).re then (1 : ℂ) else 0)) := by
    intro i hi
    by_cases he : (a i).re = (a k).re
    · simp only [ite_eq_left he]
      have hfn : (fun n => Complex.exp ((a i - ((a k).re : ℂ)) * (alignedRadii (a k).im n : ℂ))) = fun _ => 1 :=
        funext (alignedRadii_equal_projection (ha k hk) (ha i hi) he)
      rw [hfn]
      exact tendsto_const_nhds
    · simp only [ite_eq_right he]
      exact alignedRadii_lower_projection (lt_of_le_of_ne (hmax i hi) he)
  simpa only [← Finset.sum_filter, Finset.sum_const, nsmul_eq_mul, mul_one] using tendsto_finsetSum s ht

/-- A nonzero exponential normalization identifies the logarithmic slope. -/
theorem log_norm_slope_of_normalized_limit {r : ℕ → ℝ} {F : ℕ → ℂ} {h : ℝ} {c : ℂ}
    (hr : Tendsto r atTop atTop) (hc : c ≠ 0)
    (hf : Tendsto (fun n => Complex.exp (-((h * r n : ℝ) : ℂ)) * F n) atTop (𝓝 c)) :
    Tendsto (fun n => Real.log ‖F n‖ / r n) atTop (𝓝 h) := by
  have ht : Tendsto (fun n => Real.log ‖Complex.exp (-((h * r n : ℝ) : ℂ)) * F n‖) atTop (𝓝 (Real.log ‖c‖)) := by
    exact (Real.continuousAt_log (norm_ne_zero_iff.mpr hc)).tendsto.comp hf.norm
  have hlim : Tendsto (fun n => h + Real.log ‖Complex.exp (-((h * r n : ℝ) : ℂ)) * F n‖ / r n) atTop (𝓝 h) := by
    simpa using tendsto_const_nhds.add (ht.div_atTop hr)
  apply hlim.congr'
  filter_upwards [hr.eventually (eventually_gt_atTop (0 : ℝ)), hf.eventually_ne hc] with n hn hne
  have hFn : F n ≠ 0 := (mul_ne_zero_iff.mp hne).2
  rw [norm_mul, Complex.norm_exp, Complex.neg_re, Complex.ofReal_re,
    Real.log_mul (Real.exp_ne_zero _) (norm_ne_zero_iff.mpr hFn), Real.log_exp]
  field_simp
  ring

end
end Komorebi.PaperIV
