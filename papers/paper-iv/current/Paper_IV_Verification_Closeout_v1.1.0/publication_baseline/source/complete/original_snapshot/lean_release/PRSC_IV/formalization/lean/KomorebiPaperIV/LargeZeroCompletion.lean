/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroEnumeration
import KomorebiPaperIV.SignedDerivativeAsymptotics

namespace Komorebi.PaperIV
noncomputable section
open Metric Set

/-- The derivative error is measured at the actual zero, with the same
exponential rate as in the manuscript, rather than only at its lattice center. -/
theorem signedPositiveZero_derivative_asymptotic {N : ℕ} (hN : 3 ≤ N) :
    ∃ C : ℝ, 0 < C ∧ ∃ M : ℕ, ∀ m ≥ M,
      |‖deriv (canonicalSignedDenominator N) (signedPositiveZero N m : ℂ)‖ /
        ((2 * Real.sin (Real.pi / N) / N) *
          Real.exp (Real.cos (Real.pi / N) * signedPositiveZero N m)) - 1| ≤
        C * Real.exp (-signedPolygonGap N * signedPositiveZero N m) := by
  obtain ⟨C0, _, M, hM⟩ := signedPositiveZero_local_strings hN
  let B := (‖signedZeroFrequency N‖ + 2) / ‖signedZeroFrequency N‖
  let S := signedRemainderScale N
  let r := 1 / ‖signedZeroFrequency N‖
  have hB : 0 < B := div_pos (by positivity) (norm_pos_iff.mpr (signedZeroFrequency_ne_zero (by omega)))
  have hS : 0 < S := by
    have h := signedRemainderEnvelope_pos hN 0
    simpa only [signedRemainderEnvelope, mul_zero, Real.exp_zero, mul_one] using h
  refine ⟨B * S * Real.exp (signedPolygonGap N * r), by positivity, M, ?_⟩
  intro m hm
  have hx := (hM m hm).1
  have hbound := canonicalSignedDenominator_derivative_modulus_error hN
    (signedZeroCenter_ge_radius (by omega) m) hx.2.2 hx.2.1
  have hdelta : signedPositiveZero N m - signedZeroCenter N m ≤ r := by
    have hb : |signedPositiveZero N m - signedZeroCenter N m| ≤ r := by
      simpa only [mem_closedBall, dist_eq_norm, ← Complex.ofReal_sub, Complex.norm_real,
        Real.norm_eq_abs] using hx.2.2
    exact (le_abs_self _).trans hb
  have hg : 0 < signedPolygonGap N := signedPolygonGap_pos hN
  have he : Real.exp (-signedPolygonGap N * signedZeroCenter N m) ≤
      Real.exp (signedPolygonGap N * r) *
        Real.exp (-signedPolygonGap N * signedPositiveZero N m) := by
    rw [← Real.exp_add]
    apply Real.exp_le_exp.mpr
    nlinarith
  calc
    _ ≤ B * (S * Real.exp (-signedPolygonGap N * signedZeroCenter N m)) := hbound
    _ ≤ B * (S * (Real.exp (signedPolygonGap N * r) *
        Real.exp (-signedPolygonGap N * signedPositiveZero N m))) := by gcongr
    _ = _ := by ring

/-- Unique root-of-unity orbit and lattice index for every sufficiently large
zero, with one fixed cutoff for the named sequence. -/
theorem signedPositiveZero_unique_global_strings {N : ℕ} (hN : 3 ≤ N) (K : ℕ) :
    ∃ M : ℕ, K ≤ M ∧ ∃ R : ℝ, 0 < R ∧ ∀ z : ℂ, R ≤ ‖z‖ → canonicalSignedDenominator N z = 0 →
      ∃! p : {p : Fin N × ℕ // M ≤ p.2},
        z = canonicalPrimitiveRoot N ^ p.val.1.val * (signedPositiveZero N p.val.2 : ℂ) := by
  let : NeZero N := ⟨by omega⟩
  have hn : 0 < N := by omega
  have homega := canonicalPrimitiveRoot_isPrimitive hn
  obtain ⟨C, _, M0, hM0⟩ := signedPositiveZero_local_strings hN
  let M := max M0 K
  have hM (m : ℕ) (hm : M ≤ m) := hM0 m (le_trans (le_max_left M0 K) hm)
  obtain ⟨R, hR, hex⟩ := canonicalSignedDenominator_large_zero_orbits hN M
  have hinj : Set.InjOn (signedPositiveZero N) (Ici M) := by
    intro m hm n hn he
    apply signedZeroCenter_disk_index_unique (by omega) (hM m hm).1.2.2
    rw [he]
    exact (hM n hn).1.2.2
  refine ⟨M, le_max_right M0 K, R, hR, ?_⟩
  intro z hz hz0
  obtain ⟨k, _, m, hm, hb, _, _, _⟩ := hex z hz hz0
  have hu : (canonicalPrimitiveRoot N ^ k) ^ N = 1 := by
    rw [← pow_mul, Nat.mul_comm, pow_mul, homega.pow_eq_one, one_pow]
  have he := (hM m hm).2.2.2 (canonicalPrimitiveRoot N ^ k * z)
    ⟨hb, by rw [canonicalSignedDenominator_rotation hn hu]; exact hz0⟩
  have hui : ((canonicalPrimitiveRoot N ^ k)⁻¹) ^ N = 1 := by rw [inv_pow, hu, inv_one]
  obtain ⟨j, hj, hjinv⟩ := homega.eq_pow_of_pow_eq_one hui
  have hu0 : canonicalPrimitiveRoot N ^ k ≠ 0 := by intro h; simp [h, hn.ne'] at hu
  have hzrep : z = canonicalPrimitiveRoot N ^ j * (signedPositiveZero N m : ℂ) := by
    rw [← he, hjinv, ← mul_assoc, inv_mul_cancel₀ hu0, one_mul]
  refine ⟨⟨(⟨j, hj⟩, m), hm⟩, hzrep, ?_⟩
  intro p hp
  have heq : canonicalPrimitiveRoot N ^ p.val.1.val * (signedPositiveZero N p.val.2 : ℂ) =
      canonicalPrimitiveRoot N ^ j * (signedPositiveZero N m : ℂ) := hp.symm.trans hzrep
  have hnorm := congrArg norm heq
  simp only [norm_mul, norm_pow, homega.norm'_eq_one hn.ne', one_pow, one_mul,
    Complex.norm_real, Real.norm_eq_abs, abs_of_pos (signedPositiveZero_pos (N := N) (by omega) _)] at hnorm
  have hmidx : p.val.2 = m := hinj p.property hm hnorm
  have hkidx : p.val.1.val = j := by
    apply homega.pow_inj p.val.1.isLt hj
    rw [hmidx] at heq
    exact mul_right_cancel₀ (Complex.ofReal_ne_zero.mpr (ne_of_gt (signedPositiveZero_pos (by omega) m))) heq
  apply Subtype.ext
  exact Prod.ext (Fin.ext hkidx) hmidx

/-- The exact derivative covariance at each named zero. -/
theorem signedPositiveZero_derivative_rotation {N : ℕ} (hN : 2 ≤ N) (k m : ℕ) :
    deriv (canonicalSignedDenominator N)
      (canonicalPrimitiveRoot N ^ k * (signedPositiveZero N m : ℂ)) =
      (canonicalPrimitiveRoot N ^ k)⁻¹ *
        deriv (canonicalSignedDenominator N) (signedPositiveZero N m : ℂ) := by
  have hn : 0 < N := by omega
  have hu : (canonicalPrimitiveRoot N ^ k) ^ N = 1 := by
    rw [← pow_mul, Nat.mul_comm, pow_mul, (canonicalPrimitiveRoot_isPrimitive hn).pow_eq_one, one_pow]
  have h := canonicalSignedDenominator_derivative_rotation hn hu (signedPositiveZero N m : ℂ)
  have hu0 : canonicalPrimitiveRoot N ^ k ≠ 0 := by intro h; simp [h, hn.ne'] at hu
  apply (mul_right_cancel₀ hu0)
  rw [h]
  field_simp

/-- The complete large-zero statement: one tail cutoff, unique global orbit
indices, actual-zero displacement, derivative covariance, and the derivative
modulus estimate at the actual zero. All constants are derived. -/
theorem canonicalSignedDenominator_large_zero_strings {N : ℕ} (hN : 3 ≤ N) :
    0 < signedPolygonGap N ∧ ∃ M : ℕ, ∃ C : ℝ, 0 < C ∧ ∃ B : ℝ, 0 < B ∧ ∃ R : ℝ, 0 < R ∧
      (∀ m ≥ M, isLocalizedPositiveZero N m (signedPositiveZero N m) ∧
        analyticOrderAt (canonicalSignedDenominator N) (signedPositiveZero N m : ℂ) = 1 ∧
        |signedPositiveZero N m - signedZeroCenter N m| ≤
          C * Real.exp (-signedPolygonGap N * signedZeroCenter N m) ∧
        |‖deriv (canonicalSignedDenominator N) (signedPositiveZero N m : ℂ)‖ /
          ((2 * Real.sin (Real.pi / N) / N) *
            Real.exp (Real.cos (Real.pi / N) * signedPositiveZero N m)) - 1| ≤
          B * Real.exp (-signedPolygonGap N * signedPositiveZero N m)) ∧
      (∀ z : ℂ, R ≤ ‖z‖ → canonicalSignedDenominator N z = 0 →
        ∃! p : {p : Fin N × ℕ // M ≤ p.2},
          z = canonicalPrimitiveRoot N ^ p.val.1.val * (signedPositiveZero N p.val.2 : ℂ)) ∧
      (∀ k m : ℕ, deriv (canonicalSignedDenominator N)
        (canonicalPrimitiveRoot N ^ k * (signedPositiveZero N m : ℂ)) =
        (canonicalPrimitiveRoot N ^ k)⁻¹ *
          deriv (canonicalSignedDenominator N) (signedPositiveZero N m : ℂ)) := by
  obtain ⟨C, hC, M0, hM0⟩ := signedPositiveZero_local_strings hN
  obtain ⟨B, hB, M1, hM1⟩ := signedPositiveZero_derivative_asymptotic hN
  obtain ⟨M, hM, R, hR, hex⟩ := signedPositiveZero_unique_global_strings hN (max M0 M1)
  refine ⟨signedPolygonGap_pos hN, M, C, hC, B, hB, R, hR, ?_, hex,
    signedPositiveZero_derivative_rotation (by omega)⟩
  intro m hm
  have hm0 := hM0 m (le_trans (le_max_left M0 M1) (le_trans hM hm))
  have hm1 := hM1 m (le_trans (le_max_right M0 M1) (le_trans hM hm))
  exact ⟨hm0.1, hm0.2.1, hm0.2.2.1, hm1⟩

end
end Komorebi.PaperIV
