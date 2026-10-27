/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SignedSectorConfinement

/-! # Exhaustion of the large zeros within the fundamental sector -/

namespace Komorebi.PaperIV
noncomputable section
open Metric

theorem signedSectorWidth_pos {N : ℕ} (hN : 3 ≤ N) : 0 < signedSectorWidth N := by
  apply div_pos (Real.log_pos _) (mul_pos (by norm_num) (signed_sine_pos (by omega)))
  exact_mod_cast (show 1 < N - 1 by omega)

/-- The canonical remainder is uniformly small on any fixed horizontal strip. -/
theorem signedRemainder_eventually_small_on_strip {N : ℕ} (hN : 3 ≤ N)
    {Y ε : ℝ} (hY : 0 ≤ Y) (hε : 0 < ε) (q : ℕ) :
    ∃ T : ℝ, 0 ≤ T ∧ ∀ z : ℂ, T ≤ z.re → |z.im| ≤ Y →
      ‖signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) q z‖ ≤ ε := by
  obtain ⟨T, hT, hb⟩ := signedRemainder_eventually_small_on_disks hN hY hε q
  refine ⟨T, hY.trans hT, ?_⟩
  intro z hx hy
  apply hb z.re hx z
  rw [mem_closedBall, dist_eq_norm]
  have he : z - (z.re : ℂ) = (z.im : ℂ) * Complex.I := by apply Complex.ext <;> simp
  rw [he, norm_mul, Complex.norm_I, mul_one, Complex.norm_real, Real.norm_eq_abs]
  exact hy

/-- The integer cancellation centers in the perturbation theorem are real. -/
theorem signed_integer_center {N : ℕ} (hN : 2 ≤ N) (k : ℤ) :
    oddExponentialCenter k / signedZeroFrequency N =
      (((Real.pi / Real.sin (Real.pi / N)) * ((k : ℝ) + 1 / 2) : ℝ) : ℂ) := by
  have hs : (Real.sin (Real.pi / N) : ℂ) ≠ 0 := by exact_mod_cast (signed_sine_pos hN).ne'
  rw [signedZeroFrequency, canonicalSignedVertex_adjacent_difference (by omega)]
  unfold oddExponentialCenter
  push_cast
  field_simp

/-- Beyond an explicit existence threshold, every sector zero lies in one of
the already constructed natural-index disks, and is real and simple. -/
theorem canonicalSignedDenominator_sector_exhaustion {N : ℕ} (hN : 3 ≤ N) (m0 : ℕ) :
    ∃ X : ℝ, 0 < X ∧ ∀ z : ℂ, signedFundamentalSector N z → X ≤ z.re →
      canonicalSignedDenominator N z = 0 → ∃ m : ℕ, m0 ≤ m ∧
        z ∈ closedBall (signedZeroCenter N m : ℂ) (1 / ‖signedZeroFrequency N‖) ∧
        z.im = 0 ∧ 0 < z.re ∧ analyticOrderAt (canonicalSignedDenominator N) z = 1 ∧
        ∀ w : ℂ, w ∈ closedBall (signedZeroCenter N m : ℂ) (1 / ‖signedZeroFrequency N‖) ∧
          canonicalSignedDenominator N w = 0 → w = z := by
  let a := signedZeroFrequency N
  let r : ℝ := 1 / ‖a‖
  let A : ℝ := Real.pi / Real.sin (Real.pi / N)
  have ha : 0 < ‖a‖ := norm_pos_iff.mpr (signedZeroFrequency_ne_zero (by omega))
  have hr : 0 < r := one_div_pos.mpr ha
  have hA : 0 < A := div_pos Real.pi_pos (signed_sine_pos (by omega))
  obtain ⟨T, hTr, hlocal⟩ := canonicalSignedDenominator_eventual_local_zero hN
  obtain ⟨T0, hT0, hb0⟩ := signedRemainder_eventually_small_on_strip hN
    (signedSectorWidth_pos hN).le (by norm_num : (0 : ℝ) < 1 / 2) 0
  obtain ⟨T1, hT1, hb1⟩ := signedRemainder_eventually_small_on_strip hN
    (signedSectorWidth_pos hN).le (div_pos ha (by norm_num : (0 : ℝ) < 4)) 1
  let B := max T (A * ((m0 : ℝ) + 1 / 2))
  let X := max (B + r) (max T0 T1) + 1
  have hB : 0 < B := lt_of_lt_of_le (hr.trans_le hTr) (le_max_left _ _)
  refine ⟨X, by dsimp [X]; have := le_max_left (B + r) (max T0 T1); linarith, ?_⟩
  intro z hsector hx hz0
  have hstrip := canonicalSignedDenominator_sector_zero_bound hN hsector hz0
  have hxB : B + r < z.re := by
    have := le_max_left (B + r) (max T0 T1)
    dsimp [X] at hx
    linarith
  have hx0 : T0 ≤ z.re := by
    have := le_max_right (B + r) (max T0 T1)
    have := le_max_left T0 T1
    dsimp [X] at hx
    linarith
  have hx1 : T1 ≤ z.re := by
    have := le_max_right (B + r) (max T0 T1)
    have := le_max_right T0 T1
    dsimp [X] at hx
    linarith
  have h0 := hb0 z hx0 hstrip
  have h1 := hb1 z hx1 hstrip
  obtain ⟨k, hk, _⟩ := canonicalSignedDenominator_zero_lattice_distance hN hz0 h0
  let t : ℝ := A * ((k : ℝ) + 1 / 2)
  have hdist : ‖z - (t : ℂ)‖ ≤ r := by
    rw [signed_integer_center (by omega)] at hk
    apply hk.trans
    change (3 / 2 : ℝ) * _ / ‖a‖ ≤ 1 / ‖a‖
    apply div_le_div_of_nonneg_right _ ha.le
    nlinarith
  have ht : B < t := by
    have hh := (Complex.abs_re_le_norm (z - (t : ℂ))).trans hdist
    simp only [Complex.sub_re, Complex.ofReal_re] at hh
    have := (abs_le.mp hh).2
    linarith
  have hk0 : 0 ≤ k := by
    by_contra hh
    have hk1 : (k : ℝ) ≤ -1 := by exact_mod_cast (show k ≤ -1 by omega)
    have ht0 : 0 < t := hB.trans ht
    dsimp [t] at ht0
    nlinarith
  let m : ℕ := k.toNat
  have hkm : (m : ℝ) = k := by exact_mod_cast (Int.toNat_of_nonneg hk0)
  have hcenter : signedZeroCenter N m = t := by
    change A * ((m : ℝ) + 1 / 2) = A * ((k : ℝ) + 1 / 2)
    rw [hkm]
  have hm0 : m0 ≤ m := by
    have hh := lt_of_le_of_lt (le_max_right T (A * ((m0 : ℝ) + 1 / 2))) ht
    have hmm : (m0 : ℝ) < m := by dsimp [t] at hh; rw [← hkm] at hh; nlinarith
    exact_mod_cast hmm.le
  have hzball : z ∈ closedBall (signedZeroCenter N m : ℂ) r := by
    simpa only [mem_closedBall, dist_eq_norm, hcenter] using hdist
  obtain ⟨w, hw, hu⟩ := hlocal (signedZeroCenter N m)
    (by rw [hcenter]; exact (le_max_left _ _).trans ht.le)
    (signedZeroCenter_cancellation (by omega) m)
  have hzw : z = w := hu z ⟨hzball, hz0⟩
  have huz : ∀ v : ℂ, v ∈ closedBall (signedZeroCenter N m : ℂ) r ∧
      canonicalSignedDenominator N v = 0 → v = z := by
    intro v hv
    exact (hu v hv).trans hzw.symm
  refine ⟨m, hm0, hzball, canonicalSignedDenominator_unique_zero_real (by omega) hzball hz0 huz,
    by linarith, canonicalSignedDenominator_local_zero_simple hN hz0 h0 h1, huz⟩

end
end Komorebi.PaperIV
