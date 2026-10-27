/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SignedSectorExhaustion

/-! # Rotation and global exhaustion of the large denominator zeros -/

namespace Komorebi.PaperIV
noncomputable section
open Metric

/-- The actual entire denominator is invariant under every Nth root of unity. -/
theorem canonicalSignedDenominator_rotation {N : ℕ} (hN : 0 < N)
    {u : ℂ} (hu : u ^ N = 1) (z : ℂ) :
    canonicalSignedDenominator N (u * z) = canonicalSignedDenominator N z := by
  have hleft := hasSum_entireSigned hN hN (canonicalPrimitiveRoot_isPrimitive hN)
    (canonicalSignedRoot_pow hN) (u * z)
  have hright := hasSum_entireSigned hN hN (canonicalPrimitiveRoot_isPrimitive hN)
    (canonicalSignedRoot_pow hN) z
  unfold canonicalSignedDenominator
  apply hleft.unique
  convert hright using 1
  funext n
  by_cases hn : n % N = 0
  · have hp : u ^ n = 1 := by rw [pow_eq_pow_mod n hu, hn, pow_zero]
    simp only [mul_pow, hp, one_mul]
  · simp [coeff_signedSection, signedSectionCoeff, hn]

/-- Polar angles between the two tie-sector boundaries satisfy the Cartesian
sector inequalities, with a uniform positive lower bound for the real part. -/
theorem signedFundamentalSector_polar {N : ℕ} (hN : 3 ≤ N)
    {r θ : ℝ} (hr : 0 ≤ r) (hθ : |θ| ≤ Real.pi / N) :
    signedFundamentalSector N ((r : ℂ) * Complex.exp ((θ : ℂ) * Complex.I)) ∧
      r * Real.cos (Real.pi / N) ≤
        ((r : ℂ) * Complex.exp ((θ : ℂ) * Complex.I)).re := by
  let a := Real.pi / N
  have hn : (3 : ℝ) ≤ N := by exact_mod_cast hN
  have ha : 0 < a := div_pos Real.pi_pos (by linarith)
  have he : a * N = Real.pi := div_mul_cancel₀ _ (by linarith)
  have hap : a ≤ Real.pi := by nlinarith [Real.pi_pos]
  have hc : Real.cos a ≤ Real.cos θ := by
    have hh := Real.cos_le_cos_of_nonneg_of_le_pi (abs_nonneg θ) hap hθ
    simpa only [Real.cos_abs] using hh
  have hre : ((r : ℂ) * Complex.exp ((θ : ℂ) * Complex.I)).re = r * Real.cos θ := by
    rw [Complex.re_ofReal_mul, Complex.exp_ofReal_mul_I_re]
  have him : ((r : ℂ) * Complex.exp ((θ : ℂ) * Complex.I)).im = r * Real.sin θ := by
    rw [Complex.im_ofReal_mul, Complex.exp_ofReal_mul_I_im]
  have hcos : 0 < Real.cos θ := lt_of_lt_of_le (signed_cosine_pos hN) hc
  have hs : |Real.sin θ| * Real.cos a ≤ Real.cos θ * Real.sin a := by
    have ht : |θ| ≤ Real.pi := hθ.trans hap
    have hsin : |Real.sin θ| = Real.sin |θ| := by
      by_cases hh : 0 ≤ θ
      · rw [abs_of_nonneg hh, abs_of_nonneg (Real.sin_nonneg_of_mem_Icc ⟨hh, (abs_le.mp ht).2⟩)]
      · rw [abs_of_neg (lt_of_not_ge hh), Real.sin_neg]
        have hnθ : Real.sin θ ≤ 0 := by
          have hh' := Real.sin_nonneg_of_mem_Icc ⟨(by linarith : 0 ≤ -θ), (by linarith [(abs_le.mp ht).1] : -θ ≤ Real.pi)⟩
          rw [Real.sin_neg] at hh'
          linarith
        rw [abs_of_nonpos hnθ]
    have hdiff := Real.sin_nonneg_of_mem_Icc (show a - |θ| ∈ Set.Icc 0 Real.pi by
      constructor <;> linarith [abs_nonneg θ])
    rw [Real.sin_sub, Real.cos_abs, ← hsin] at hdiff
    nlinarith
  refine ⟨⟨by rw [hre]; positivity, ?_⟩, ?_⟩
  · rw [him, hre, abs_mul, abs_of_nonneg hr]
    nlinarith [mul_le_mul_of_nonneg_left hs hr]
  · rw [hre]
    exact mul_le_mul_of_nonneg_left hc hr

/-- Every complex number can be rotated into the fundamental sector by an
actual Nth root of unity. The rotated real part controls its original norm. -/
theorem exists_signed_sector_rotation {N : ℕ} (hN : 3 ≤ N) (z : ℂ) :
    ∃ u : ℂ, u ^ N = 1 ∧ ‖u‖ = 1 ∧ signedFundamentalSector N (u * z) ∧
      ‖z‖ * Real.cos (Real.pi / N) ≤ (u * z).re := by
  let a : ℝ := Real.pi / N
  have hn : (0 : ℝ) < N := by exact_mod_cast (show 0 < N by omega)
  have ha : 0 < a := div_pos Real.pi_pos hn
  obtain ⟨k, hk, _⟩ := existsUnique_add_zsmul_mem_Ioc (show 0 < 2 * a by positivity) z.arg (-a)
  rw [zsmul_eq_mul] at hk
  let θ := z.arg + (k : ℝ) * (2 * a)
  have hθ : |θ| ≤ a := by
    rcases hk with ⟨hlo, hhi⟩
    apply abs_le.mpr
    constructor <;> dsimp [θ] <;> linarith
  let u := Complex.exp ((((k : ℝ) * (2 * a) : ℝ) : ℂ) * Complex.I)
  have hu : u ^ N = 1 := by
    dsimp [u]
    rw [← Complex.exp_nat_mul]
    have harg : (N : ℂ) * (((((k : ℝ) * (2 * a) : ℝ) : ℂ)) * Complex.I) =
        (k : ℂ) * (2 * (Real.pi : ℂ) * Complex.I) := by
      dsimp [a]
      push_cast
      field_simp [show (N : ℂ) ≠ 0 by exact_mod_cast hn.ne']
    rw [harg, Complex.exp_int_mul_two_pi_mul_I]
  have hnorm : ‖u‖ = 1 := by dsimp [u]; exact Complex.norm_exp_ofReal_mul_I _
  have hz : u * z = (‖z‖ : ℂ) * Complex.exp ((θ : ℂ) * Complex.I) := by
    conv_lhs => rw [← Complex.norm_mul_exp_arg_mul_I z]
    dsimp [u, θ]
    rw [mul_left_comm, ← Complex.exp_add]
    congr 2
    push_cast
    ring
  have hsector := signedFundamentalSector_polar hN (norm_nonneg z) hθ
  rw [← hz] at hsector
  exact ⟨u, hu, hnorm, hsector.1, hsector.2⟩

/-- Every sufficiently large zero is a rotation of one of the real simple
zeros constructed near the natural-index cancellation centers. -/
theorem canonicalSignedDenominator_global_exhaustion {N : ℕ} (hN : 3 ≤ N) (m0 : ℕ) :
    ∃ R : ℝ, 0 < R ∧ ∀ z : ℂ, R ≤ ‖z‖ → canonicalSignedDenominator N z = 0 →
      ∃ u : ℂ, ∃ m : ℕ, u ^ N = 1 ∧ ‖u‖ = 1 ∧ m0 ≤ m ∧
        canonicalSignedDenominator N (u * z) = 0 ∧
        u * z ∈ closedBall (signedZeroCenter N m : ℂ) (1 / ‖signedZeroFrequency N‖) ∧
        (u * z).im = 0 ∧ 0 < (u * z).re ∧
        analyticOrderAt (canonicalSignedDenominator N) (u * z) = 1 ∧
        ∀ w : ℂ, w ∈ closedBall (signedZeroCenter N m : ℂ) (1 / ‖signedZeroFrequency N‖) ∧
          canonicalSignedDenominator N w = 0 → w = u * z := by
  obtain ⟨X, hX, hex⟩ := canonicalSignedDenominator_sector_exhaustion hN m0
  have hc := signed_cosine_pos hN
  refine ⟨X / Real.cos (Real.pi / N), div_pos hX hc, ?_⟩
  intro z hz hz0
  obtain ⟨u, hu, hunorm, hsector, hreal⟩ := exists_signed_sector_rotation hN z
  have hx : X ≤ (u * z).re := ((div_le_iff₀ hc).mp hz).trans hreal
  have hu0 : canonicalSignedDenominator N (u * z) = 0 := by
    rw [canonicalSignedDenominator_rotation (by omega) hu, hz0]
  obtain ⟨m, hm, hball, him, hpos, hs, huniq⟩ := hex (u * z) hsector hx hu0
  exact ⟨u, m, hu, hunorm, hm, hu0, hball, him, hpos, hs, huniq⟩

end
end Komorebi.PaperIV
