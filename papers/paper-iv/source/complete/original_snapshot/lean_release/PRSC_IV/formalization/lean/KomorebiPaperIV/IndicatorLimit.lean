/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.AlignedExponentialRadii
import KomorebiPaperIV.UniformDominantSectors

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

/-- The finite exponential representation gives the sharp directional bound. -/
theorem canonicalSignedDenominator_indicator_upper {N : ℕ} (hN : 0 < N)
    (θ : ℝ) {r : ℝ} (hr : 0 ≤ r) :
    ‖canonicalSignedDenominator N ((r : ℂ) * rayDirection θ)‖ ≤ Real.exp (r * signedIndicator N hN θ) := by
  unfold canonicalSignedDenominator
  rw [entireSigned_zero_eq_average, norm_mul, norm_inv, Complex.norm_natCast]
  have hb (i : ℕ) (hi : i ∈ Finset.range N) :
      ‖Complex.exp (canonicalSignedVertex N i * ((r : ℂ) * rayDirection θ))‖ ≤
        Real.exp (r * signedIndicator N hN θ) := by
    rw [Complex.norm_exp]
    apply Real.exp_le_exp.mpr
    have he : (canonicalSignedVertex N i * ((r : ℂ) * rayDirection θ)).re =
        r * signedProjection N θ i := by
      rw [show canonicalSignedVertex N i * ((r : ℂ) * rayDirection θ) =
        (r : ℂ) * (canonicalSignedVertex N i * rayDirection θ) by ring, Complex.re_ofReal_mul]
      rfl
    rw [he]
    exact mul_le_mul_of_nonneg_left (signedProjection_le_indicator hN (Finset.mem_range.mp hi) θ) hr
  calc
    _ ≤ (N : ℝ)⁻¹ * ∑ i ∈ Finset.range N, ‖Complex.exp (canonicalSignedVertex N i * ((r : ℂ) * rayDirection θ))‖ :=
      mul_le_mul_of_nonneg_left (norm_sum_le _ _) (by positivity)
    _ ≤ (N : ℝ)⁻¹ * ∑ _i ∈ Finset.range N, Real.exp (r * signedIndicator N hN θ) :=
      mul_le_mul_of_nonneg_left (Finset.sum_le_sum hb) (by positivity)
    _ = _ := by simp [hN.ne']

theorem canonicalSignedDenominator_log_indicator_upper {N : ℕ} (hN : 2 ≤ N)
    (θ : ℝ) {r : ℝ} (hr : 0 < r) :
    Real.log ‖canonicalSignedDenominator N ((r : ℂ) * rayDirection θ)‖ / r ≤
      signedIndicator N (by omega) θ := by
  apply (div_le_iff₀ hr).mpr
  by_cases hz : canonicalSignedDenominator N ((r : ℂ) * rayDirection θ) = 0
  · simp only [hz, norm_zero, Real.log_zero]
    exact mul_nonneg (signedIndicator_nonneg hN θ) hr.le
  · have h := (Real.log_le_iff_le_exp (norm_pos_iff.mpr hz)).mpr
      (canonicalSignedDenominator_indicator_upper (show 0 < N by omega) θ hr.le)
    simpa only [mul_comm] using h

theorem canonicalSignedDenominator_real_normalization (N : ℕ) (θ h r : ℝ) :
    Complex.exp (-((h * r : ℝ) : ℂ)) * canonicalSignedDenominator N ((r : ℂ) * rayDirection θ) =
      (N : ℂ)⁻¹ * ∑ i ∈ Finset.range N,
        Complex.exp ((canonicalSignedVertex N i * rayDirection θ - (h : ℂ)) * (r : ℂ)) := by
  unfold canonicalSignedDenominator
  rw [entireSigned_zero_eq_average, mul_left_comm]
  congr 1
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  rw [← Complex.exp_add]
  congr 1
  dsimp [canonicalSignedVertex]
  push_cast
  ring

/-- The lower indicator sequence exists in every direction, including ties. -/
theorem canonicalSignedDenominator_indicator_sequence {N : ℕ} (hN : 0 < N) (θ : ℝ) :
    ∃ r : ℕ → ℝ, Tendsto r atTop atTop ∧
      Tendsto (fun n => Real.log ‖canonicalSignedDenominator N ((r n : ℂ) * rayDirection θ)‖ / r n)
        atTop (𝓝 (signedIndicator N hN θ)) ∧
      ∀ᶠ n in atTop, canonicalSignedDenominator N ((r n : ℂ) * rayDirection θ) ≠ 0 := by
  let a : ℕ → ℂ := fun i => canonicalSignedVertex N i * rayDirection θ
  obtain ⟨k, hk, he⟩ := (Finset.range N).exists_mem_eq_sup' ⟨0, Finset.mem_range.mpr hN⟩ (signedProjection N θ)
  have hmax : ∀ i ∈ Finset.range N, (a i).re ≤ (a k).re :=
    fun i hi => (signedProjection_le_indicator hN (Finset.mem_range.mp hi) θ).trans_eq he
  have ht := finite_unit_exponential_aligned_limit hk
    (a := a) (fun i _ => by simp [a, norm_canonicalSignedVertex, norm_rayDirection]) hmax
  let r := alignedRadii (a k).im
  let c : ℂ := (N : ℂ)⁻¹ * ((Finset.range N).filter (fun i => (a i).re = (a k).re)).card
  have hcard : 0 < ((Finset.range N).filter (fun i => (a i).re = (a k).re)).card :=
    Finset.card_pos.mpr ⟨k, Finset.mem_filter.mpr ⟨hk, rfl⟩⟩
  have hc : c ≠ 0 := mul_ne_zero
    (inv_ne_zero (by exact_mod_cast hN.ne')) (by exact_mod_cast hcard.ne')
  have hnorm : Tendsto (fun n => Complex.exp (-(((a k).re * r n : ℝ) : ℂ)) *
      canonicalSignedDenominator N ((r n : ℂ) * rayDirection θ)) atTop (𝓝 c) := by
    simpa only [canonicalSignedDenominator_real_normalization] using! ht.const_mul (N : ℂ)⁻¹
  refine ⟨r, alignedRadii_tendsto _, ?_, ?_⟩
  · have hslope := log_norm_slope_of_normalized_limit (alignedRadii_tendsto _) hc hnorm
    have he' : signedIndicator N hN θ = (a k).re := he
    rw [he']
    exact hslope
  · exact (hnorm.eventually_ne hc).mono (fun n hn => (mul_ne_zero_iff.mp hn).2)

/-- A sharp upper bound and a convergent lower sequence determine a limsup. -/
theorem limsup_eq_of_upper_and_sequence {f : ℝ → ℝ} {h : ℝ} {l : Filter ℝ}
    (hu : ∀ᶠ r in l, f r ≤ h) {r : ℕ → ℝ}
    (hr : Tendsto r atTop l) (hf : Tendsto (fun n => f (r n)) atTop (𝓝 h)) :
    limsup f l = h := by
  have hleast (b : ℝ) (hb : ∀ᶠ x in l, f x ≤ b) : h ≤ b :=
    le_of_tendsto hf (hr.eventually hb)
  exact le_antisymm (limsup_le_of_le ⟨h, hleast⟩ hu) (le_limsup_of_le ⟨h, hu⟩ hleast)

/-- The exact indicator equality in Theorem 11.4, with no omitted tie directions. -/
theorem canonicalSignedDenominator_indicator {N : ℕ} (hN : 2 ≤ N) (θ : ℝ) :
    limsup (fun r : ℝ => Real.log ‖canonicalSignedDenominator N ((r : ℂ) * rayDirection θ)‖ / r) atTop =
      signedIndicator N (by omega) θ := by
  obtain ⟨r, hr, hf, _⟩ := canonicalSignedDenominator_indicator_sequence (show 0 < N by omega) θ
  exact limsup_eq_of_upper_and_sequence
    ((eventually_gt_atTop (0 : ℝ)).mono (fun r hr => canonicalSignedDenominator_log_indicator_upper hN θ hr)) hr hf

/-- The same indicator on the classical logarithm domain. This avoids relying
on Lean's totalized value of log(0) at zeros along a ray. -/
theorem canonicalSignedDenominator_indicator_nonzero_radii {N : ℕ} (hN : 2 ≤ N) (θ : ℝ) :
    limsup (fun r : ℝ => Real.log ‖canonicalSignedDenominator N ((r : ℂ) * rayDirection θ)‖ / r)
      (atTop ⊓ principal {r : ℝ | canonicalSignedDenominator N ((r : ℂ) * rayDirection θ) ≠ 0}) =
      signedIndicator N (by omega) θ := by
  obtain ⟨r, hr, hf, hn⟩ := canonicalSignedDenominator_indicator_sequence (show 0 < N by omega) θ
  apply limsup_eq_of_upper_and_sequence _ (tendsto_inf.mpr ⟨hr, tendsto_principal.mpr hn⟩) hf
  exact ((eventually_gt_atTop (0 : ℝ)).mono
    (fun r hr => canonicalSignedDenominator_log_indicator_upper hN θ hr)).filter_mono inf_le_left

end
end Komorebi.PaperIV
