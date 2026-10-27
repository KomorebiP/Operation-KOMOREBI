/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SignedGlobalExhaustion

namespace Komorebi.PaperIV
noncomputable section
open Metric

theorem signedZeroFrequency_norm {N : ℕ} (hN : 2 ≤ N) :
    ‖signedZeroFrequency N‖ = 2 * Real.sin (Real.pi / N) := by
  rw [signedZeroFrequency, canonicalSignedVertex_adjacent_difference (by omega), norm_mul,
    norm_mul, Complex.norm_I, mul_one, Complex.norm_real, Real.norm_eq_abs,
    abs_of_pos (signed_sine_pos hN)]
  norm_num

/-- Rotation preserves the actual analytic multiplicity. -/
theorem canonicalSignedDenominator_order_rotation {N : ℕ} (hN : 0 < N)
    {u : ℂ} (hu : u ^ N = 1) (z : ℂ) :
    analyticOrderAt (canonicalSignedDenominator N) z =
      analyticOrderAt (canonicalSignedDenominator N) (u * z) := by
  have hu0 : u ≠ 0 := by intro h; simp [h, Nat.ne_of_gt hN] at hu
  have hg : AnalyticAt ℂ (fun w : ℂ => u * w) z := by fun_prop
  have hd : deriv (fun w : ℂ => u * w) z = u := by
    simpa only [id_eq, mul_one] using ((hasDerivAt_id z).const_mul u).deriv
  have he : canonicalSignedDenominator N ∘ (fun w : ℂ => u * w) = canonicalSignedDenominator N :=
    funext (canonicalSignedDenominator_rotation hN hu)
  have hh := analyticOrderAt_comp_of_deriv_ne_zero (f := canonicalSignedDenominator N) hg
    (by rw [hd]; exact hu0)
  rwa [he] at hh

/-- The derivative transforms by the inverse rotation. -/
theorem canonicalSignedDenominator_derivative_rotation {N : ℕ} (hN : 0 < N)
    {u : ℂ} (hu : u ^ N = 1) (z : ℂ) :
    deriv (canonicalSignedDenominator N) (u * z) * u = deriv (canonicalSignedDenominator N) z := by
  have hd := (analyticAt_entireSigned N 0 (canonicalPrimitiveRoot N) (canonicalSignedRoot N)
    (u * z)).differentiableAt.hasDerivAt
  have hg := (hasDerivAt_id z).const_mul u
  have hc := hd.comp z hg
  have he : (fun w : ℂ => canonicalSignedDenominator N (u * w)) = canonicalSignedDenominator N :=
    funext (canonicalSignedDenominator_rotation hN hu)
  change HasDerivAt (fun w : ℂ => canonicalSignedDenominator N (u * w))
    (deriv (canonicalSignedDenominator N) (u * z) * (u * 1)) z at hc
  rw [he, mul_one] at hc
  exact hc.deriv.symm

/-- A nonzero complex number has at most one unit-modulus rotation to the
positive real axis. -/
theorem positive_real_rotation_unique {z u v : ℂ} (hz : z ≠ 0)
    (hu : ‖u‖ = 1) (hv : ‖v‖ = 1)
    (hui : (u * z).im = 0) (hvi : (v * z).im = 0)
    (hur : 0 < (u * z).re) (hvr : 0 < (v * z).re) : u = v := by
  have hreal (w : ℂ) (hi : w.im = 0) : w = (w.re : ℂ) := by
    apply Complex.ext <;> simp [hi]
  have hnorm (w : ℂ) (hi : w.im = 0) (hr : 0 < w.re) : ‖w‖ = w.re := by
    conv_lhs => rw [hreal w hi]
    rw [Complex.norm_real, Real.norm_eq_abs, abs_of_pos hr]
  have he : u * z = v * z := by
    apply Complex.ext
    · rw [← hnorm (u * z) hui hur, ← hnorm (v * z) hvi hvr, norm_mul, norm_mul, hu, hv]
    · rw [hui, hvi]
  exact mul_right_cancel₀ hz he

/-- The fixed-radius disks around distinct natural lattice centers are disjoint. -/
theorem signedZeroCenter_disk_index_unique {N m n : ℕ} (hN : 2 ≤ N) {z : ℂ}
    (hm : z ∈ closedBall (signedZeroCenter N m : ℂ) (1 / ‖signedZeroFrequency N‖))
    (hn : z ∈ closedBall (signedZeroCenter N n : ℂ) (1 / ‖signedZeroFrequency N‖)) : m = n := by
  have hs := signed_sine_pos hN
  have hdist : ‖(signedZeroCenter N m : ℂ) - (signedZeroCenter N n : ℂ)‖ ≤
      2 / ‖signedZeroFrequency N‖ := by
    have h := dist_triangle (signedZeroCenter N m : ℂ) z (signedZeroCenter N n : ℂ)
    have hm' := mem_closedBall.mp hm
    have hn' := mem_closedBall.mp hn
    rw [dist_comm z (signedZeroCenter N m : ℂ)] at hm'
    rw [dist_eq_norm] at h
    calc
      _ ≤ _ := h
      _ ≤ 1 / ‖signedZeroFrequency N‖ + 1 / ‖signedZeroFrequency N‖ := add_le_add hm' hn'
      _ = _ := by ring
  rw [← Complex.ofReal_sub, Complex.norm_real, Real.norm_eq_abs, signedZeroFrequency_norm hN] at hdist
  have he : signedZeroCenter N m - signedZeroCenter N n =
      (Real.pi / Real.sin (Real.pi / N)) * ((m : ℝ) - n) := by unfold signedZeroCenter; ring
  rw [he, abs_mul, abs_of_pos (div_pos Real.pi_pos hs)] at hdist
  have hmul := (le_div_iff₀ (mul_pos (by norm_num) hs)).mp hdist
  have hcancel : (Real.pi / Real.sin (Real.pi / N)) * |(m : ℝ) - n| *
      (2 * Real.sin (Real.pi / N)) = 2 * Real.pi * |(m : ℝ) - n| := by field_simp
  rw [hcancel] at hmul
  by_contra hne
  have habs : 1 ≤ |(m : ℝ) - n| := by
    rcases lt_or_gt_of_ne hne with h | h
    · have hh : (m : ℝ) + 1 ≤ n := by exact_mod_cast (show m + 1 ≤ n by omega)
      rw [abs_of_nonpos (by linarith)]
      linarith
    · have hh : (n : ℝ) + 1 ≤ m := by exact_mod_cast (show n + 1 ≤ m by omega)
      rw [abs_of_nonneg (by linarith)]
      linarith
  nlinarith [Real.two_le_pi]

/-- In the manuscript's canonical finite set of rotations, all sufficiently
large zeros belong to the real strings and are simple at their original point. -/
theorem canonicalSignedDenominator_large_zero_orbits {N : ℕ} (hN : 3 ≤ N) (m0 : ℕ) :
    ∃ R : ℝ, 0 < R ∧ ∀ z : ℂ, R ≤ ‖z‖ → canonicalSignedDenominator N z = 0 →
      ∃ k < N, ∃ m : ℕ, m0 ≤ m ∧
        canonicalPrimitiveRoot N ^ k * z ∈
          closedBall (signedZeroCenter N m : ℂ) (1 / ‖signedZeroFrequency N‖) ∧
        (canonicalPrimitiveRoot N ^ k * z).im = 0 ∧
        0 < (canonicalPrimitiveRoot N ^ k * z).re ∧
        analyticOrderAt (canonicalSignedDenominator N) z = 1 := by
  let : NeZero N := ⟨by omega⟩
  obtain ⟨R, hR, hex⟩ := canonicalSignedDenominator_global_exhaustion hN m0
  refine ⟨R, hR, ?_⟩
  intro z hz hz0
  obtain ⟨u, m, hu, _, hm, _, hball, him, hpos, hs, _⟩ := hex z hz hz0
  obtain ⟨k, hk, he⟩ := (canonicalPrimitiveRoot_isPrimitive (by omega : 0 < N)).eq_pow_of_pow_eq_one hu
  refine ⟨k, hk, m, hm, he.symm ▸ hball, he.symm ▸ him, he.symm ▸ hpos, ?_⟩
  rw [canonicalSignedDenominator_order_rotation (by omega) hu]
  exact hs

end
end Komorebi.PaperIV
