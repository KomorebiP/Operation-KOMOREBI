/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SignedGlobalExhaustion

namespace Komorebi.PaperIV
noncomputable section

/-- The manuscript's argument-based sector implies the Cartesian inequalities. -/
theorem signedFundamentalSector_of_arg {N : ℕ} (hN : 3 ≤ N) {z : ℂ}
    (hz : |z.arg| ≤ Real.pi / N) : signedFundamentalSector N z := by
  have h := (signedFundamentalSector_polar hN (norm_nonneg z) hz).1
  simpa only [Complex.norm_mul_exp_arg_mul_I] using h

/-- One constant controls the first three remainder jets on a fixed strip. -/
theorem canonicalSignedRemainder_three_jet_bound {N : ℕ} (hN : 3 ≤ N)
    {Y : ℝ} {z : ℂ} (hx : 0 ≤ z.re) (hy : |z.im| ≤ Y) {q : ℕ} (hq : q ≤ 2) :
    ‖signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) q z‖ ≤
      (((N - 2 : ℕ) : ℝ) * 4 * Real.exp (2 * Y)) * Real.exp (-signedPolygonGap N * z.re) := by
  have hpow : (2 : ℝ) ^ q ≤ 4 := by
    have hh : q = 0 ∨ q = 1 ∨ q = 2 := by omega
    rcases hh with rfl | rfl | rfl <;> norm_num
  have hb := canonicalSignedRemainder_strip_bound hN hx hy q
  calc
    _ ≤ ((N - 2 : ℕ) : ℝ) * 2 ^ q * Real.exp (-signedPolygonGap N * z.re + 2 * Y) := hb
    _ ≤ ((N - 2 : ℕ) : ℝ) * 4 * Real.exp (-signedPolygonGap N * z.re + 2 * Y) := by
      gcongr
    _ = _ := by rw [Real.exp_add]; ring

/-- The full argument-sector, normalization, and three-jet conclusion of
manuscript Lemma 11.5, with actual derived positive constants. -/
theorem canonicalSignedDenominator_two_term_dominance {N : ℕ} (hN : 3 ≤ N) :
    ∃ Y R C : ℝ, 0 < Y ∧ 0 < R ∧ 0 < C ∧
      (∀ z : ℂ, |z.arg| ≤ Real.pi / N → R ≤ z.re →
        canonicalSignedDenominator N z = 0 → |z.im| ≤ Y) ∧
      (∀ z : ℂ, (N : ℂ) * Complex.exp (-(canonicalSignedVertex N (N - 1) * z)) *
        canonicalSignedDenominator N z =
        1 + Complex.exp (signedZeroFrequency N * z) +
          signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) 0 z) ∧
      (∀ z : ℂ, R ≤ z.re → |z.im| ≤ Y → ∀ q : ℕ, q ≤ 2 →
        ‖signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) q z‖ ≤
          C * Real.exp (-signedPolygonGap N * z.re)) := by
  let Y := signedSectorWidth N
  refine ⟨Y, 1, ((N - 2 : ℕ) : ℝ) * 4 * Real.exp (2 * Y),
    signedSectorWidth_pos hN, by norm_num, ?_, ?_, ?_, ?_⟩
  · have hn : 0 < N - 2 := by omega
    positivity
  · intro z harg _ hz
    exact canonicalSignedDenominator_sector_zero_bound hN (signedFundamentalSector_of_arg hN harg) hz
  · intro z
    exact signed_two_term_normalization (by omega) _ _ z
  · intro z hx hy q hq
    exact canonicalSignedRemainder_three_jet_bound hN (by linarith) hy hq

end
end Komorebi.PaperIV
