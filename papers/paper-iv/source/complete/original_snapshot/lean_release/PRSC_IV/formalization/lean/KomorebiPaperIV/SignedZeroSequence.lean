/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ReducedZeros

namespace Komorebi.PaperIV
noncomputable section
open Metric

/-- A positive real zero in the fixed disk around the `m`th cancellation center. -/
def isLocalizedPositiveZero (N m : ℕ) (t : ℝ) : Prop :=
  0 < t ∧ canonicalSignedDenominator N (t : ℂ) = 0 ∧
    (t : ℂ) ∈ closedBall (signedZeroCenter N m : ℂ) (1 / ‖signedZeroFrequency N‖)

/-- An actual root is chosen when one exists; the default is used only before the proven tail. -/
def signedPositiveZero (N m : ℕ) : ℝ := by
  classical
  exact if h : ∃ t, isLocalizedPositiveZero N m t then h.choose else signedZeroCenter N m

theorem signedPositiveZero_spec {N m : ℕ} (h : ∃ t, isLocalizedPositiveZero N m t) :
    isLocalizedPositiveZero N m (signedPositiveZero N m) := by
  unfold signedPositiveZero
  rw [dite_eq_left h]
  exact h.choose_spec

theorem signedPositiveZero_eq_of_unique {N m : ℕ} {z : ℂ}
    (hb : z ∈ closedBall (signedZeroCenter N m : ℂ) (1 / ‖signedZeroFrequency N‖))
    (hz : canonicalSignedDenominator N z = 0) (hi : z.im = 0) (hp : 0 < z.re)
    (hu : ∀ w : ℂ, w ∈ closedBall (signedZeroCenter N m : ℂ) (1 / ‖signedZeroFrequency N‖) ∧
      canonicalSignedDenominator N w = 0 → w = z) : (signedPositiveZero N m : ℂ) = z := by
  have he : (z.re : ℂ) = z := by apply Complex.ext <;> simp [hi]
  have hh : isLocalizedPositiveZero N m z.re := ⟨hp, he.symm ▸ hz, he.symm ▸ hb⟩
  have hs := signedPositiveZero_spec ⟨z.re, hh⟩
  exact hu _ ⟨hs.2.2, hs.2.1⟩

/-- A fixed real sequence, rather than separate existential witnesses, realizes the local strings. -/
theorem signedPositiveZero_local_strings {N : ℕ} (hN : 3 ≤ N) :
    ∃ C : ℝ, 0 < C ∧ ∃ m0 : ℕ, ∀ m ≥ m0,
      isLocalizedPositiveZero N m (signedPositiveZero N m) ∧
      analyticOrderAt (canonicalSignedDenominator N) (signedPositiveZero N m : ℂ) = 1 ∧
      |signedPositiveZero N m - signedZeroCenter N m| ≤
        C * Real.exp (-signedPolygonGap N * signedZeroCenter N m) ∧
      ∀ w : ℂ, w ∈ closedBall (signedZeroCenter N m : ℂ) (1 / ‖signedZeroFrequency N‖) ∧
        canonicalSignedDenominator N w = 0 → w = (signedPositiveZero N m : ℂ) := by
  obtain ⟨C, hC, m0, hm0⟩ := canonicalSignedDenominator_local_strings hN
  refine ⟨C, hC, m0, ?_⟩
  intro m hm
  obtain ⟨z, hb, hz, hi, hp, ho, he, hu⟩ := hm0 m hm
  have hroot := signedPositiveZero_eq_of_unique hb hz hi hp hu
  have hr : signedPositiveZero N m = z.re := by simpa using congrArg Complex.re hroot
  refine ⟨⟨by rw [hr]; exact hp, by rw [hroot]; exact hz, by rw [hroot]; exact hb⟩,
    by rw [hroot]; exact ho, ?_, ?_⟩
  · rw [← hroot, ← Complex.ofReal_sub, Complex.norm_real, Real.norm_eq_abs] at he
    exact he
  · intro w hw; rw [hroot]; exact hu w hw

/-- The real sequence exhausts all large zeros after root-of-unity rotation. -/
theorem signedPositiveZero_global_strings {N : ℕ} (hN : 3 ≤ N) :
    ∃ m0 : ℕ, ∃ R : ℝ, 0 < R ∧ ∀ z : ℂ, R ≤ ‖z‖ → canonicalSignedDenominator N z = 0 →
      ∃ k < N, ∃ m ≥ m0, canonicalPrimitiveRoot N ^ k * z = (signedPositiveZero N m : ℂ) := by
  obtain ⟨C, _, m0, hm0⟩ := signedPositiveZero_local_strings hN
  obtain ⟨R, hR, hex⟩ := canonicalSignedDenominator_large_zero_orbits hN m0
  refine ⟨m0, R, hR, ?_⟩
  intro z hz hz0
  obtain ⟨k, hk, m, hm, hb, _, _, _⟩ := hex z hz hz0
  have hu : (canonicalPrimitiveRoot N ^ k) ^ N = 1 := by
    rw [← pow_mul, Nat.mul_comm, pow_mul, (canonicalPrimitiveRoot_isPrimitive (by omega)).pow_eq_one, one_pow]
  refine ⟨k, hk, m, hm, (hm0 m hm).2.2.2 _ ⟨hb, ?_⟩⟩
  rw [canonicalSignedDenominator_rotation (by omega) hu]; exact hz0

theorem signedZeroCenter_ge_radius {N : ℕ} (hN : 2 ≤ N) (m : ℕ) :
    1 / ‖signedZeroFrequency N‖ ≤ signedZeroCenter N m := by
  rw [signedZeroFrequency_norm hN, signedZeroCenter]
  have hs := signed_sine_pos hN
  have hm : (0 : ℝ) ≤ m := Nat.cast_nonneg m
  apply (div_le_iff₀ (mul_pos (by norm_num) hs)).mpr
  have he : Real.pi / Real.sin (Real.pi / N) * ((m : ℝ) + 1 / 2) *
      (2 * Real.sin (Real.pi / N)) = Real.pi * (2 * m + 1) := by field_simp
  rw [he]
  nlinarith [Real.two_le_pi]

theorem signedPositiveZero_pos {N : ℕ} (hN : 2 ≤ N) (m : ℕ) :
    0 < signedPositiveZero N m := by
  classical
  by_cases h : ∃ t, isLocalizedPositiveZero N m t
  · exact (signedPositiveZero_spec h).1
  · rw [signedPositiveZero, dite_eq_right h]
    exact lt_of_lt_of_le (one_div_pos.mpr (norm_pos_iff.mpr (signedZeroFrequency_ne_zero hN)))
      (signedZeroCenter_ge_radius hN m)

/-- Distinct lattice disks give distinct real zeros. -/
theorem signedPositiveZero_injective_on_tail {N : ℕ} (hN : 3 ≤ N) :
    ∃ m0 : ℕ, Set.InjOn (signedPositiveZero N) (Set.Ici m0) := by
  obtain ⟨C, _, m0, hm0⟩ := signedPositiveZero_local_strings hN
  refine ⟨m0, ?_⟩
  intro m hm n hn he
  apply signedZeroCenter_disk_index_unique (by omega : 2 ≤ N) (hm0 m hm).1.2.2
  rw [he]
  exact (hm0 n hn).1.2.2

/-- The reduced zero sequence is the actual `N`th power of the positive denominator zero. -/
def reducedPositiveZero (N m : ℕ) : ℝ := signedPositiveZero N m ^ N

/-- Every sufficiently large reduced zero is an entry of the fixed power sequence. -/
theorem reducedPositiveZero_global_strings {N : ℕ} (hN : 3 ≤ N) :
    ∃ m0 : ℕ, ∃ R : ℝ, 0 < R ∧ ∀ w : ℂ, R ≤ ‖w‖ → entireReducedDenominator N w = 0 →
      ∃ m ≥ m0, w = (reducedPositiveZero N m : ℂ) := by
  obtain ⟨m0, R, hR, hex⟩ := signedPositiveZero_global_strings hN
  refine ⟨m0, R ^ N, pow_pos hR N, ?_⟩
  intro w hw hw0
  obtain ⟨z, hz⟩ := exists_complex_nth_root (by omega : 0 < N) w
  have hr : R ≤ ‖z‖ := by
    by_contra h
    have hp := pow_lt_pow_left₀ (lt_of_not_ge h) (norm_nonneg z) (by omega : N ≠ 0)
    have hn : ‖z‖ ^ N = ‖w‖ := by rw [← norm_pow, hz]
    linarith
  have hd : canonicalSignedDenominator N z = 0 := by
    rw [canonicalSignedDenominator_eq_reduced_power (by omega), hz]; exact hw0
  obtain ⟨k, _, m, hm, he⟩ := hex z hr hd
  have hu : (canonicalPrimitiveRoot N ^ k) ^ N = 1 := by
    rw [← pow_mul, Nat.mul_comm, pow_mul, (canonicalPrimitiveRoot_isPrimitive (by omega)).pow_eq_one, one_pow]
  refine ⟨m, hm, ?_⟩
  have hh := congrArg (fun x : ℂ => x ^ N) he
  simpa only [mul_pow, hu, one_mul, hz, reducedPositiveZero, Complex.ofReal_pow] using hh

theorem reducedPositiveZero_injective_on_tail {N : ℕ} (hN : 3 ≤ N) :
    ∃ m0 : ℕ, Set.InjOn (reducedPositiveZero N) (Set.Ici m0) := by
  obtain ⟨m0, hm0⟩ := signedPositiveZero_injective_on_tail hN
  refine ⟨m0, ?_⟩
  intro m hm n hn he
  apply hm0 hm hn
  exact (pow_left_strictMonoOn₀ (by omega : N ≠ 0)).injOn
    (le_of_lt (signedPositiveZero_pos (by omega) m))
    (le_of_lt (signedPositiveZero_pos (by omega) n)) he

/-- Quantitative reduced-zero displacement, including the polynomial loss in the power map. -/
theorem reducedPositiveZero_local_strings {N : ℕ} (hN : 3 ≤ N) :
    ∃ C : ℝ, 0 < C ∧ ∃ m0 : ℕ, ∀ m ≥ m0,
      0 < reducedPositiveZero N m ∧
      entireReducedDenominator N (reducedPositiveZero N m : ℂ) = 0 ∧
      analyticOrderAt (entireReducedDenominator N) (reducedPositiveZero N m : ℂ) = 1 ∧
      |reducedPositiveZero N m - signedZeroCenter N m ^ N| ≤
        C * signedZeroCenter N m ^ (N - 1) * Real.exp (-signedPolygonGap N * signedZeroCenter N m) := by
  obtain ⟨C, hC, m0, hm0⟩ := signedPositiveZero_local_strings hN
  refine ⟨C * N * 2 ^ (N - 1), by positivity, m0, ?_⟩
  intro m hm
  obtain ⟨hs, ho, he, _⟩ := hm0 m hm
  have ht : 0 < signedZeroCenter N m := by
    exact lt_of_lt_of_le (one_div_pos.mpr (norm_pos_iff.mpr (signedZeroFrequency_ne_zero (by omega))))
      (signedZeroCenter_ge_radius (by omega) m)
  have hb : |signedPositiveZero N m - signedZeroCenter N m| ≤ 1 / ‖signedZeroFrequency N‖ := by
    simpa only [mem_closedBall, dist_eq_norm, ← Complex.ofReal_sub, Complex.norm_real, Real.norm_eq_abs] using hs.2.2
  have hu : signedPositiveZero N m ≤ 2 * signedZeroCenter N m := by
    have hh := (le_abs_self (signedPositiveZero N m - signedZeroCenter N m)).trans hb
    have hr := signedZeroCenter_ge_radius (by omega : 2 ≤ N) m
    linarith
  refine ⟨pow_pos hs.1 N, ?_, ?_, ?_⟩
  · rw [reducedPositiveZero, Complex.ofReal_pow, ← canonicalSignedDenominator_eq_reduced_power (by omega)]
    exact hs.2.1
  · rw [reducedPositiveZero, Complex.ofReal_pow,
      ← canonicalSignedDenominator_order_eq_reduced (by omega) (Complex.ofReal_ne_zero.mpr (ne_of_gt hs.1))]
    exact ho
  · calc
      _ ≤ |signedPositiveZero N m - signedZeroCenter N m| * N *
          max |signedPositiveZero N m| |signedZeroCenter N m| ^ (N - 1) := abs_pow_sub_pow_le _ _ _
      _ ≤ (C * Real.exp (-signedPolygonGap N * signedZeroCenter N m)) * N *
          (2 * signedZeroCenter N m) ^ (N - 1) := by
        gcongr
        rw [abs_of_pos hs.1, abs_of_pos ht]
        exact max_le hu (by linarith)
      _ = _ := by rw [mul_pow]; ring

end
end Komorebi.PaperIV
