/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.RegularPolygonGap
import KomorebiPaperIV.ZeroPerturbation
import Mathlib.Topology.Algebra.InfiniteSum.Constructions

/-! # Actual large local zero strings of the signed denominator

This module applies the contraction theorem to the canonical finite sum and
derives its smallness hypotheses. Global exclusion outside these disks is not
assumed or asserted.
-/

namespace Komorebi.PaperIV
noncomputable section
open Metric

def canonicalSignedDenominator (N : ℕ) : ℂ → ℂ :=
  entireSigned N 0 (canonicalPrimitiveRoot N) (canonicalSignedRoot N)

def signedZeroFrequency (N : ℕ) : ℂ :=
  canonicalSignedRoot N - canonicalSignedVertex N (N - 1)

def signedZeroCenter (N m : ℕ) : ℝ :=
  (Real.pi / Real.sin (Real.pi / N)) * (m + 1 / 2)

theorem signed_sine_pos {N : ℕ} (hN : 2 ≤ N) : 0 < Real.sin (Real.pi / N) := by
  have hn : (2 : ℝ) ≤ N := by exact_mod_cast hN
  have hp : 0 < Real.pi / N := div_pos Real.pi_pos (by linarith)
  have he : Real.pi / N * N = Real.pi := div_mul_cancel₀ _ (by linarith)
  exact Real.sin_pos_of_pos_of_lt_pi hp (by nlinarith)

theorem signedZeroFrequency_ne_zero {N : ℕ} (hN : 2 ≤ N) : signedZeroFrequency N ≠ 0 := by
  rw [signedZeroFrequency, canonicalSignedVertex_adjacent_difference (by omega)]
  exact mul_ne_zero (mul_ne_zero (by norm_num) (by exact_mod_cast (signed_sine_pos hN).ne')) Complex.I_ne_zero

theorem signedZeroCenter_cancellation {N : ℕ} (hN : 2 ≤ N) (m : ℕ) :
    Complex.exp (signedZeroFrequency N * (signedZeroCenter N m : ℂ)) = -1 := by
  have hs : (Real.sin (Real.pi / N) : ℂ) ≠ 0 := by exact_mod_cast (signed_sine_pos hN).ne'
  have he : signedZeroFrequency N * (signedZeroCenter N m : ℂ) =
      (Real.pi : ℂ) * Complex.I + (m : ℤ) * (2 * (Real.pi : ℂ) * Complex.I) := by
    rw [signedZeroFrequency, canonicalSignedVertex_adjacent_difference (by omega)]
    unfold signedZeroCenter
    push_cast
    push_cast at hs
    field_simp [hs]
    ring
  rw [he, ← Complex.exp_pi_mul_I]
  apply Complex.exp_eq_exp_iff_exists_int.mpr
  exact ⟨(m : ℤ), rfl⟩

/-- Uniform exponential decay on a fixed-radius disk translated along the real axis. -/
theorem canonicalSignedRemainder_disk_bound {N : ℕ} (hN : 3 ≤ N)
    {t r : ℝ} (ht : r ≤ t) {z : ℂ} (hz : z ∈ closedBall (t : ℂ) r) (q : ℕ) :
    ‖signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) q z‖ ≤
      (((N - 2 : ℕ) : ℝ) * 2 ^ q * Real.exp (signedPolygonGap N * r + 2 * r)) *
        Real.exp (-signedPolygonGap N * t) := by
  have hzN : ‖z - (t : ℂ)‖ ≤ r := by simpa [mem_closedBall, dist_eq_norm] using hz
  have hreal : t - r ≤ z.re := by
    have h := (Complex.abs_re_le_norm (z - (t : ℂ))).trans hzN
    simp only [Complex.sub_re, Complex.ofReal_re] at h
    have := (abs_le.mp h).1
    linarith
  have him : |z.im| ≤ r := by
    simpa only [Complex.sub_im, Complex.ofReal_im, sub_zero] using
      (Complex.abs_im_le_norm (z - (t : ℂ))).trans hzN
  have hb := canonicalSignedRemainder_strip_bound hN (by linarith : 0 ≤ z.re) him q
  calc
    _ ≤ ((N - 2 : ℕ) : ℝ) * 2 ^ q * Real.exp (-signedPolygonGap N * z.re + 2 * r) := hb
    _ ≤ ((N - 2 : ℕ) : ℝ) * 2 ^ q *
        Real.exp ((signedPolygonGap N * r + 2 * r) + (-signedPolygonGap N * t)) := by
      apply mul_le_mul_of_nonneg_left _ (by positivity)
      apply Real.exp_le_exp.mpr
      nlinarith [signedPolygonGap_pos hN]
    _ = _ := by rw [Real.exp_add]; ring

/-- An explicit threshold exists for smallness on every translated fixed disk. -/
theorem signedRemainder_eventually_small_on_disks {N : ℕ} (hN : 3 ≤ N)
    {r ε : ℝ} (_hr : 0 ≤ r) (hε : 0 < ε) (q : ℕ) :
    ∃ T : ℝ, r ≤ T ∧ ∀ t : ℝ, T ≤ t → ∀ z ∈ closedBall (t : ℂ) r,
      ‖signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) q z‖ ≤ ε := by
  let γ := signedPolygonGap N
  let C : ℝ := ((N - 2 : ℕ) : ℝ) * 2 ^ q
  have hγ : 0 < γ := signedPolygonGap_pos hN
  have hC : 0 < C := by
    dsimp [C]
    have hn : 0 < N - 2 := by omega
    positivity
  let T := max r ((γ * r + 2 * r - Real.log (ε / C)) / γ)
  refine ⟨T, le_max_left _ _, ?_⟩
  intro t ht z hz
  have htR : r ≤ t := (le_max_left _ _).trans ht
  have hzN : ‖z - (t : ℂ)‖ ≤ r := by simpa [mem_closedBall, dist_eq_norm] using hz
  have hreal : t - r ≤ z.re := by
    have h := (Complex.abs_re_le_norm (z - (t : ℂ))).trans hzN
    simp only [Complex.sub_re, Complex.ofReal_re] at h
    have := (abs_le.mp h).1
    linarith
  have him : |z.im| ≤ r := by
    simpa only [Complex.sub_im, Complex.ofReal_im, sub_zero] using
      (Complex.abs_im_le_norm (z - (t : ℂ))).trans hzN
  have hb := canonicalSignedRemainder_strip_bound hN (by linarith : 0 ≤ z.re) him q
  have hexp : Real.exp (-γ * t + γ * r + 2 * r) ≤ ε / C := by
    apply (Real.le_log_iff_exp_le (div_pos hε hC)).mp
    have hh : (γ * r + 2 * r - Real.log (ε / C)) / γ ≤ t := (le_max_right _ _).trans ht
    have := (div_le_iff₀ hγ).mp hh
    linarith
  calc
    _ ≤ C * Real.exp (-γ * z.re + 2 * r) := hb
    _ ≤ C * Real.exp (-γ * t + γ * r + 2 * r) := by
      apply mul_le_mul_of_nonneg_left _ hC.le
      apply Real.exp_le_exp.mpr
      nlinarith
    _ ≤ C * (ε / C) := mul_le_mul_of_nonneg_left hexp hC.le
    _ = ε := by field_simp

theorem canonicalSignedDenominator_conj {N : ℕ} (hN : 0 < N) (z : ℂ) :
    canonicalSignedDenominator N (star z) = star (canonicalSignedDenominator N z) := by
  have hs := (hasSum_entireSigned hN hN (canonicalPrimitiveRoot_isPrimitive hN)
    (canonicalSignedRoot_pow hN) z).star
  have ht := hasSum_entireSigned hN hN (canonicalPrimitiveRoot_isPrimitive hN)
    (canonicalSignedRoot_pow hN) (star z)
  apply ht.unique
  convert hs using 1
  · funext n
    by_cases h : n % N = 0
    · simp [coeff_signedSection, signedSectionCoeff, h]
    · simp [coeff_signedSection, signedSectionCoeff, h]
  · rfl

/-- Every sufficiently large cancellation center has a unique actual denominator zero. -/
theorem canonicalSignedDenominator_eventual_local_zero {N : ℕ} (hN : 3 ≤ N) :
    ∃ T : ℝ, 1 / ‖signedZeroFrequency N‖ ≤ T ∧ ∀ t : ℝ, T ≤ t →
      Complex.exp (signedZeroFrequency N * (t : ℂ)) = -1 →
      ∃! z : ℂ, z ∈ closedBall (t : ℂ) (1 / ‖signedZeroFrequency N‖) ∧
        canonicalSignedDenominator N z = 0 := by
  have ha := signedZeroFrequency_ne_zero (show 2 ≤ N by omega)
  let ε := min (1 / 2 : ℝ) (‖signedZeroFrequency N‖ / 4)
  have hε : 0 < ε := lt_min (by norm_num) (div_pos (norm_pos_iff.mpr ha) (by norm_num))
  obtain ⟨T0, hT0, hb0⟩ := signedRemainder_eventually_small_on_disks hN
    (by positivity : 0 ≤ 1 / ‖signedZeroFrequency N‖) hε 0
  obtain ⟨T1, hT1, hb1⟩ := signedRemainder_eventually_small_on_disks hN
    (by positivity : 0 ≤ 1 / ‖signedZeroFrequency N‖) hε 1
  refine ⟨max T0 T1, hT0.trans (le_max_left _ _), ?_⟩
  intro t ht hc
  have h0 := hb0 t ((le_max_left _ _).trans ht)
  have h1 := hb1 t ((le_max_right _ _).trans ht)
  have hzero := perturbed_exponential_unique_zero ha hc
    (fun z hz => (h0 z hz).trans (min_le_left _ _))
    (fun z _ => hasDerivAt_finiteExponentialRemainder _ _ _ 0 z)
    (fun z hz => (h1 z hz).trans (min_le_right _ _))
  convert hzero using 1
  funext z
  congr 1
  exact propext (signed_two_term_zero_iff (show 2 ≤ N by omega)
    (canonicalPrimitiveRoot N) (canonicalSignedRoot N) z)

/-- A unique zero in a disk centered on the real axis is itself real. -/
theorem canonicalSignedDenominator_unique_zero_real {N : ℕ} (hN : 0 < N)
    {t r : ℝ} {z : ℂ} (hz : z ∈ closedBall (t : ℂ) r)
    (hz0 : canonicalSignedDenominator N z = 0)
    (hu : ∀ w : ℂ, w ∈ closedBall (t : ℂ) r ∧ canonicalSignedDenominator N w = 0 → w = z) :
    z.im = 0 := by
  have hzstar : star z ∈ closedBall (t : ℂ) r := by
    have he : star z - (t : ℂ) = star (z - (t : ℂ)) := by simp
    simpa only [mem_closedBall, dist_eq_norm, he, norm_star] using hz
  have heq := hu (star z) ⟨hzstar, by rw [canonicalSignedDenominator_conj hN, hz0, star_zero]⟩
  have him := congrArg Complex.im heq
  change -z.im = z.im at him
  linarith

/-- Simplicity transfers from the normalized exponential sum to the actual denominator. -/
theorem canonicalSignedDenominator_local_zero_simple {N : ℕ} (hN : 3 ≤ N)
    {z : ℂ} (hz : canonicalSignedDenominator N z = 0)
    (h0 : ‖signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 0 z‖ ≤ 1 / 2)
    (h1 : ‖signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 1 z‖ ≤
      ‖signedZeroFrequency N‖ / 4) :
    analyticOrderAt (canonicalSignedDenominator N) z = 1 := by
  let R := signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 0
  let P := fun w => (N : ℂ) * Complex.exp (-(canonicalSignedVertex N (N - 1) * w))
  have hR : AnalyticAt ℂ R z := analyticAt_finiteExponentialRemainder _ _ _ _ _
  have hdR : deriv R z =
      signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 1 z :=
    (hasDerivAt_finiteExponentialRemainder _ _ _ _ _).deriv
  have hzero : 1 + Complex.exp (signedZeroFrequency N * z) + R z = 0 :=
    (signed_two_term_zero_iff (by omega) _ _ z).mp hz
  have hs := perturbed_exponential_zero_order_one (signedZeroFrequency_ne_zero (by omega))
    hR hzero h0 (by rw [hdR]; exact h1)
  have he : (fun w => 1 + Complex.exp (signedZeroFrequency N * w) + R w) =
      fun w => P w * canonicalSignedDenominator N w := by
    funext w
    exact (signed_two_term_normalization (by omega) _ _ w).symm
  have hP : AnalyticAt ℂ P z := by dsimp [P]; fun_prop
  have hD : AnalyticAt ℂ (canonicalSignedDenominator N) z := analyticAt_entireSigned _ _ _ _ _
  have hP0 : analyticOrderAt P z = 0 := hP.analyticOrderAt_eq_zero.mpr
    (mul_ne_zero (by exact_mod_cast (show N ≠ 0 by omega)) (Complex.exp_ne_zero _))
  rw [he] at hs
  change analyticOrderAt (P * canonicalSignedDenominator N) z = 1 at hs
  rw [analyticOrderAt_mul hP hD, hP0, zero_add] at hs
  exact hs

/-- There are positive real simple zeros near every sufficiently large lattice center.
This proves existence of the strings, without a claim that they exhaust all large zeros. -/
theorem canonicalSignedDenominator_eventual_positive_simple_zeros {N : ℕ} (hN : 3 ≤ N) :
    ∃ m0 : ℕ, ∀ m : ℕ, m0 ≤ m → ∃ z : ℂ,
      z ∈ closedBall (signedZeroCenter N m : ℂ) (1 / ‖signedZeroFrequency N‖) ∧
      canonicalSignedDenominator N z = 0 ∧ z.im = 0 ∧ 0 < z.re ∧
      analyticOrderAt (canonicalSignedDenominator N) z = 1 ∧
      ∀ w : ℂ, w ∈ closedBall (signedZeroCenter N m : ℂ) (1 / ‖signedZeroFrequency N‖) ∧
        canonicalSignedDenominator N w = 0 → w = z := by
  have ha := signedZeroFrequency_ne_zero (show 2 ≤ N by omega)
  let r := 1 / ‖signedZeroFrequency N‖
  obtain ⟨T, _, hT⟩ := canonicalSignedDenominator_eventual_local_zero hN
  obtain ⟨T0, _, hT0⟩ := signedRemainder_eventually_small_on_disks hN
    (by positivity : 0 ≤ r) (by norm_num : (0 : ℝ) < 1 / 2) 0
  obtain ⟨T1, _, hT1⟩ := signedRemainder_eventually_small_on_disks hN
    (by positivity : 0 ≤ r) (div_pos (norm_pos_iff.mpr ha) (by norm_num : (0 : ℝ) < 4)) 1
  let A := Real.pi / Real.sin (Real.pi / N)
  have hA : 0 < A := div_pos Real.pi_pos (signed_sine_pos (by omega))
  let B := max T (max T0 (max T1 r))
  obtain ⟨m0, hm0⟩ := exists_nat_gt (B / A)
  refine ⟨m0, ?_⟩
  intro m hm
  have hmm : (m0 : ℝ) ≤ m := by exact_mod_cast hm
  have hB : B < signedZeroCenter N m := by
    have hh := (div_lt_iff₀ hA).mp hm0
    change B < A * ((m : ℝ) + 1 / 2)
    nlinarith
  have ht : T ≤ signedZeroCenter N m := (le_max_left _ _).trans hB.le
  have ht0 : T0 ≤ signedZeroCenter N m := (le_trans (le_max_left _ _) (le_max_right _ _)).trans hB.le
  have ht1 : T1 ≤ signedZeroCenter N m :=
    (le_trans (le_max_left _ _) (le_trans (le_max_right _ _) (le_max_right _ _))).trans hB.le
  have htr : r < signedZeroCenter N m :=
    lt_of_le_of_lt (le_trans (le_max_right _ _) (le_trans (le_max_right _ _) (le_max_right _ _))) hB
  obtain ⟨z, ⟨hz, hz0⟩, hu⟩ := hT (signedZeroCenter N m) ht (signedZeroCenter_cancellation (by omega) m)
  refine ⟨z, hz, hz0, canonicalSignedDenominator_unique_zero_real (by omega) hz hz0 hu, ?_, ?_, hu⟩
  · have h := (Complex.abs_re_le_norm (z - (signedZeroCenter N m : ℂ))).trans
      (show ‖z - (signedZeroCenter N m : ℂ)‖ ≤ r by simpa [r, mem_closedBall, dist_eq_norm] using hz)
    simp only [Complex.sub_re, Complex.ofReal_re] at h
    have := (abs_le.mp h).1
    linarith
  · exact canonicalSignedDenominator_local_zero_simple hN hz0
      (hT0 _ ht0 z hz) (hT1 _ ht1 z hz)

/-- Quantified exponentially small displacement for a localized denominator zero. -/
theorem canonicalSignedDenominator_local_zero_exponential_distance {N : ℕ} (hN : 3 ≤ N)
    {t : ℝ} (ht : 1 / ‖signedZeroFrequency N‖ ≤ t)
    (hc : Complex.exp (signedZeroFrequency N * (t : ℂ)) = -1)
    (hsmall : ∀ w ∈ closedBall (t : ℂ) (1 / ‖signedZeroFrequency N‖),
      ‖signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 0 w‖ ≤ 1 / 2)
    {z : ℂ} (hz : z ∈ closedBall (t : ℂ) (1 / ‖signedZeroFrequency N‖))
    (hz0 : canonicalSignedDenominator N z = 0) :
    ‖z - (t : ℂ)‖ ≤
      ((3 / 2 : ℝ) * ((N - 2 : ℕ) : ℝ) *
        Real.exp (signedPolygonGap N * (1 / ‖signedZeroFrequency N‖) + 2 * (1 / ‖signedZeroFrequency N‖)) /
          ‖signedZeroFrequency N‖) * Real.exp (-signedPolygonGap N * t) := by
  have hd := perturbed_exponential_pointwise_distance (signedZeroFrequency_ne_zero (by omega))
    hc hsmall hz ((signed_two_term_zero_iff (by omega) _ _ z).mp hz0)
  have hb := canonicalSignedRemainder_disk_bound hN ht hz 0
  simp only [pow_zero, mul_one] at hb
  apply hd.trans
  calc
    _ ≤ (3 / 2 : ℝ) *
        ((((N - 2 : ℕ) : ℝ) * Real.exp (signedPolygonGap N * (1 / ‖signedZeroFrequency N‖) +
          2 * (1 / ‖signedZeroFrequency N‖))) * Real.exp (-signedPolygonGap N * t)) /
          ‖signedZeroFrequency N‖ := by gcongr
    _ = _ := by ring

/-- The positive real simple zero strings have the manuscript's exponential location rate.
Completeness of these strings among all large complex zeros remains a separate theorem. -/
theorem canonicalSignedDenominator_local_strings {N : ℕ} (hN : 3 ≤ N) :
    ∃ C : ℝ, 0 < C ∧ ∃ m0 : ℕ, ∀ m : ℕ, m0 ≤ m → ∃ z : ℂ,
      z ∈ closedBall (signedZeroCenter N m : ℂ) (1 / ‖signedZeroFrequency N‖) ∧
      canonicalSignedDenominator N z = 0 ∧ z.im = 0 ∧ 0 < z.re ∧
      analyticOrderAt (canonicalSignedDenominator N) z = 1 ∧
      ‖z - (signedZeroCenter N m : ℂ)‖ ≤ C * Real.exp (-signedPolygonGap N * signedZeroCenter N m) ∧
      ∀ w : ℂ, w ∈ closedBall (signedZeroCenter N m : ℂ) (1 / ‖signedZeroFrequency N‖) ∧
        canonicalSignedDenominator N w = 0 → w = z := by
  have ha := signedZeroFrequency_ne_zero (show 2 ≤ N by omega)
  let r := 1 / ‖signedZeroFrequency N‖
  let C := (3 / 2 : ℝ) * ((N - 2 : ℕ) : ℝ) * Real.exp (signedPolygonGap N * r + 2 * r) /
    ‖signedZeroFrequency N‖
  have hC : 0 < C := by
    dsimp [C]
    have hn : 0 < N - 2 := by omega
    have := norm_pos_iff.mpr ha
    positivity
  obtain ⟨m0, hm0⟩ := canonicalSignedDenominator_eventual_positive_simple_zeros hN
  obtain ⟨T, hTr, hT⟩ := signedRemainder_eventually_small_on_disks hN
    (by positivity : 0 ≤ r) (by norm_num : (0 : ℝ) < 1 / 2) 0
  let A := Real.pi / Real.sin (Real.pi / N)
  have hA : 0 < A := div_pos Real.pi_pos (signed_sine_pos (by omega))
  obtain ⟨m1, hm1⟩ := exists_nat_gt (T / A)
  refine ⟨C, hC, max m0 m1, ?_⟩
  intro m hm
  have hmn : (m1 : ℝ) ≤ m := by exact_mod_cast (le_max_right m0 m1).trans hm
  have ht : T ≤ signedZeroCenter N m := by
    have hh := (div_lt_iff₀ hA).mp hm1
    change T ≤ A * ((m : ℝ) + 1 / 2)
    nlinarith
  obtain ⟨z, hz, hz0, hzim, hzpos, hzs, hu⟩ := hm0 m ((le_max_left _ _).trans hm)
  refine ⟨z, hz, hz0, hzim, hzpos, hzs, ?_, hu⟩
  exact canonicalSignedDenominator_local_zero_exponential_distance hN (hTr.trans ht)
    (signedZeroCenter_cancellation (by omega) m) (hT _ ht) hz hz0

/-- Every zero with a small normalized remainder is assigned to one lattice center. -/
theorem canonicalSignedDenominator_zero_lattice_distance {N : ℕ} (hN : 3 ≤ N)
    {z : ℂ} (hz : canonicalSignedDenominator N z = 0)
    (hsmall : ‖signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 0 z‖ ≤ 1 / 2) :
    ∃! k : ℤ, ‖z - oddExponentialCenter k / signedZeroFrequency N‖ ≤
      (3 / 2 : ℝ) *
        ‖signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 0 z‖ /
          ‖signedZeroFrequency N‖ := by
  have ha := signedZeroFrequency_ne_zero (show 2 ≤ N by omega)
  have hz0 := (signed_two_term_zero_iff (show 2 ≤ N by omega)
    (canonicalPrimitiveRoot N) (canonicalSignedRoot N) z).mp hz
  change 1 + Complex.exp (signedZeroFrequency N * z) +
    signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 0 z = 0 at hz0
  have he : ‖1 + Complex.exp (signedZeroFrequency N * z)‖ =
      ‖signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 0 z‖ := by
    have h : 1 + Complex.exp (signedZeroFrequency N * z) =
        -signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 0 z := by
      linear_combination hz0
    rw [h, norm_neg]
  have h := near_cancellation_unique (he.trans_le hsmall)
  rw [he] at h
  convert h using 1
  funext k
  apply propext
  have heq : z - oddExponentialCenter k / signedZeroFrequency N =
      (signedZeroFrequency N * z - oddExponentialCenter k) / signedZeroFrequency N := by
    field_simp
  rw [heq, norm_div]
  exact div_le_div_iff_of_pos_right (norm_pos_iff.mpr ha)

end
end Komorebi.PaperIV
