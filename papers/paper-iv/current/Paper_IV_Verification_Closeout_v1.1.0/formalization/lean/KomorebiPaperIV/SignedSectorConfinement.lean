/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SignedZeroLocalization

/-! # Exact confinement of zeros in the fundamental sector

The two adjacent vertices are the largest two projections throughout the
fundamental sector. This gives a strip bound without an asymptotic hypothesis.
-/

namespace Komorebi.PaperIV
noncomputable section

/-- The closed fundamental sector, expressed without a choice of argument. -/
def signedFundamentalSector (N : ℕ) (z : ℂ) : Prop :=
  0 ≤ z.re ∧ |z.im| * Real.cos (Real.pi / N) ≤ z.re * Real.sin (Real.pi / N)

theorem signed_cosine_pos {N : ℕ} (hN : 3 ≤ N) : 0 < Real.cos (Real.pi / N) := by
  have hn : (3 : ℝ) ≤ N := by exact_mod_cast hN
  have hp : 0 < Real.pi / N := div_pos Real.pi_pos (by linarith)
  have he : Real.pi / N * N = Real.pi := div_mul_cancel₀ _ (by linarith)
  apply Real.cos_pos_of_mem_Ioo
  constructor <;> nlinarith [Real.pi_pos]

/-- Cosine on a closed arc avoiding zero is bounded by its endpoint value. -/
theorem cosine_arc_upper {a θ : ℝ} (ha : 0 ≤ a) (hlo : a ≤ θ)
    (hhi : θ ≤ 2 * Real.pi - a) : Real.cos θ ≤ Real.cos a := by
  by_cases hθ : θ ≤ Real.pi
  · exact Real.cos_le_cos_of_nonneg_of_le_pi ha hθ hlo
  · have hc := Real.cos_le_cos_of_nonneg_of_le_pi ha
      (by linarith : 2 * Real.pi - θ ≤ Real.pi) (by linarith : a ≤ 2 * Real.pi - θ)
    simpa only [Real.cos_two_pi_sub] using hc

/-- A nonadjacent vertex cannot exceed the upper adjacent vertex on either
boundary of the upper half of the fundamental sector. -/
theorem canonicalSignedVertex_upper_boundary {N l : ℕ} (hN : 3 ≤ N)
    (hl : l ∈ ((Finset.range N).erase 0).erase (N - 1)) :
    (canonicalSignedVertex N l - canonicalSignedVertex N 0).re * Real.cos (Real.pi / N) -
      (canonicalSignedVertex N l - canonicalSignedVertex N 0).im * Real.sin (Real.pi / N) ≤ 0 := by
  have hi : 1 ≤ l ∧ l + 2 ≤ N := by
    simp only [Finset.mem_erase, Finset.mem_range] at hl
    omega
  have hn : (3 : ℝ) ≤ N := by exact_mod_cast hN
  have hl1 : (1 : ℝ) ≤ l := by exact_mod_cast hi.1
  have hl2 : (l : ℝ) + 2 ≤ N := by exact_mod_cast hi.2
  let a : ℝ := Real.pi / N
  have hp : 0 < a := div_pos Real.pi_pos (by linarith)
  have he : a * N = Real.pi := div_mul_cancel₀ _ (by linarith)
  have hc := cosine_arc_upper (a := 2 * a) (θ := (2 * l + 1) * a + a)
    (by positivity) (by nlinarith) (by nlinarith)
  rw [Real.cos_add] at hc
  have hdouble : Real.cos (2 * a) = Real.cos a * Real.cos a - Real.sin a * Real.sin a := by
    rw [show 2 * a = a + a by ring, Real.cos_add]
  rw [hdouble] at hc
  simp only [Complex.sub_re, Complex.sub_im, canonicalSignedVertex_re,
    canonicalSignedVertex_im, Nat.cast_zero, mul_zero, zero_add, one_mul]
  change (Real.cos ((2 * l + 1) * a) - Real.cos a) * Real.cos a -
    (Real.sin ((2 * l + 1) * a) - Real.sin a) * Real.sin a ≤ 0
  nlinarith

/-- Throughout the upper half sector every nonadjacent exponential is no
larger than the upper adjacent exponential. -/
theorem canonicalSignedVertex_upper_projection {N l : ℕ} (hN : 3 ≤ N)
    (hl : l ∈ ((Finset.range N).erase 0).erase (N - 1))
    {z : ℂ} (hz : signedFundamentalSector N z) (hy : 0 ≤ z.im) :
    ((canonicalSignedVertex N l - canonicalSignedVertex N 0) * z).re ≤ 0 := by
  let A := (canonicalSignedVertex N l - canonicalSignedVertex N 0).re
  let B := (canonicalSignedVertex N l - canonicalSignedVertex N 0).im
  let s := Real.sin (Real.pi / N)
  let c := Real.cos (Real.pi / N)
  have hs : 0 < s := signed_sine_pos (by omega)
  have hA : A ≤ 0 := by
    have hh := canonicalSignedVertex_re_gap hN hl
    rw [Complex.sub_re, canonicalSignedVertex_last_re (by omega)] at hh
    dsimp [A]
    rw [canonicalSignedVertex_re N 0]
    norm_num only [Nat.cast_zero, mul_zero, zero_add, one_mul]
    linarith [signedPolygonGap_pos hN]
  have hB : A * c - B * s ≤ 0 := canonicalSignedVertex_upper_boundary hN hl
  have hw : 0 ≤ z.re * s - z.im * c := by
    have hh := hz.2
    rw [abs_of_nonneg hy] at hh
    linarith
  have h1 := mul_nonpos_of_nonpos_of_nonneg hA hw
  have h2 := mul_nonpos_of_nonpos_of_nonneg hB hy
  rw [Complex.mul_re]
  change A * z.re - B * z.im ≤ 0
  nlinarith

/-- The lower adjacent vertex exceeds every other vertex by at least
`2 sin(pi/N) im(z)` on the upper half sector. -/
theorem canonicalSignedVertex_sector_gap {N l : ℕ} (hN : 3 ≤ N)
    (hl : l ∈ (Finset.range N).erase (N - 1))
    {z : ℂ} (hz : signedFundamentalSector N z) (hy : 0 ≤ z.im) :
    ((canonicalSignedVertex N l - canonicalSignedVertex N (N - 1)) * z).re ≤
      -(2 * Real.sin (Real.pi / N) * z.im) := by
  have hd : ((canonicalSignedVertex N 0 - canonicalSignedVertex N (N - 1)) * z).re =
      -(2 * Real.sin (Real.pi / N) * z.im) := by
    have hzero : canonicalSignedVertex N 0 = canonicalSignedRoot N := by simp [canonicalSignedVertex]
    rw [hzero, canonicalSignedVertex_adjacent_difference (by omega)]
    simp only [Complex.mul_re, Complex.mul_im, Complex.ofReal_re, Complex.ofReal_im,
      Complex.I_re, Complex.I_im, show (2 : ℂ).re = 2 from rfl,
      show (2 : ℂ).im = 0 from rfl]
    ring
  by_cases hl0 : l = 0
  · simpa only [hl0] using hd.le
  · have hmem : l ∈ ((Finset.range N).erase 0).erase (N - 1) := by
      simpa only [Finset.mem_erase] using ⟨(Finset.mem_erase.mp hl).1, hl0, (Finset.mem_erase.mp hl).2⟩
    have hb := canonicalSignedVertex_upper_projection hN hmem hz hy
    have he : ((canonicalSignedVertex N l - canonicalSignedVertex N (N - 1)) * z).re =
        ((canonicalSignedVertex N l - canonicalSignedVertex N 0) * z).re +
        ((canonicalSignedVertex N 0 - canonicalSignedVertex N (N - 1)) * z).re := by
      rw [← Complex.add_re]; congr 1; ring
    rw [he, hd]
    linarith

/-- Normalization by one exponential in a finite sum. -/
theorem finite_one_term_normalization {s : Finset ℕ} {a : ℕ → ℂ}
    {k : ℕ} (hk : k ∈ s) (z : ℂ) :
    Complex.exp (-(a k * z)) * (∑ l ∈ s, Complex.exp (a l * z)) =
      1 + ∑ l ∈ s.erase k, Complex.exp ((a l - a k) * z) := by
  rw [← Finset.sum_erase_add _ _ hk, mul_add, Finset.mul_sum]
  have he (v : ℂ) : Complex.exp (-(a k * z)) * Complex.exp (v * z) =
      Complex.exp ((v - a k) * z) := by rw [← Complex.exp_add]; congr 1; ring
  simp only [he, sub_self, zero_mul, Complex.exp_zero]
  ring

/-- A zero must balance the modulus of the normalized dominant term. -/
theorem finite_exponential_zero_balance {s : Finset ℕ} {a : ℕ → ℂ}
    {k : ℕ} (hk : k ∈ s) {z : ℂ} (hz : (∑ l ∈ s, Complex.exp (a l * z)) = 0)
    {d : ℝ} (hgap : ∀ l ∈ s.erase k, ((a l - a k) * z).re ≤ -d) :
    1 ≤ ((s.erase k).card : ℝ) * Real.exp (-d) := by
  have he := finite_one_term_normalization (a := a) hk z
  rw [hz, mul_zero] at he
  have hs : (∑ l ∈ s.erase k, Complex.exp ((a l - a k) * z)) = -1 := by
    linear_combination -he
  calc
    (1 : ℝ) = ‖∑ l ∈ s.erase k, Complex.exp ((a l - a k) * z)‖ := by rw [hs]; simp
    _ ≤ ∑ l ∈ s.erase k, ‖Complex.exp ((a l - a k) * z)‖ := norm_sum_le _ _
    _ ≤ ∑ _l ∈ s.erase k, Real.exp (-d) := Finset.sum_le_sum (fun l hl => by
      rw [Complex.norm_exp]; exact Real.exp_le_exp.mpr (hgap l hl))
    _ = _ := by simp

/-- Explicit strip width for the signed denominator. -/
def signedSectorWidth (N : ℕ) : ℝ :=
  Real.log ((N - 1 : ℕ) : ℝ) / (2 * Real.sin (Real.pi / N))

theorem canonicalSignedDenominator_upper_sector_zero_bound {N : ℕ} (hN : 3 ≤ N)
    {z : ℂ} (hz : signedFundamentalSector N z) (hy : 0 ≤ z.im)
    (hz0 : canonicalSignedDenominator N z = 0) : z.im ≤ signedSectorWidth N := by
  have hn : (N : ℂ) ≠ 0 := by exact_mod_cast (show N ≠ 0 by omega)
  have hsum : (∑ l ∈ Finset.range N, Complex.exp (canonicalSignedVertex N l * z)) = 0 := by
    unfold canonicalSignedDenominator at hz0
    rw [entireSigned_zero_eq_average] at hz0
    simpa only [canonicalSignedVertex, mul_eq_zero, inv_ne_zero hn, false_or] using hz0
  have hb := finite_exponential_zero_balance
    (k := N - 1) (Finset.mem_range.mpr (show N - 1 < N by omega)) hsum
    (fun l hl => canonicalSignedVertex_sector_gap hN hl hz hy)
  rw [Finset.card_erase_of_mem (Finset.mem_range.mpr (show N - 1 < N by omega)), Finset.card_range] at hb
  have hC : (0 : ℝ) < ((N - 1 : ℕ) : ℝ) := by exact_mod_cast (show 0 < N - 1 by omega)
  have he : Real.exp (2 * Real.sin (Real.pi / N) * z.im) ≤ ((N - 1 : ℕ) : ℝ) := by
    have hm := mul_le_mul_of_nonneg_right hb (Real.exp_nonneg (2 * Real.sin (Real.pi / N) * z.im))
    rw [mul_assoc (((N - 1 : ℕ) : ℝ)) (Real.exp _) (Real.exp _),
      ← Real.exp_add, neg_add_cancel, Real.exp_zero, mul_one, one_mul] at hm
    exact hm
  apply (le_div_iff₀ (mul_pos (by norm_num) (signed_sine_pos (by omega)))).mpr
  have hh := (Real.le_log_iff_exp_le hC).mpr he
  nlinarith

/-- Every zero in the closed fundamental sector lies in this fixed strip. -/
theorem canonicalSignedDenominator_sector_zero_bound {N : ℕ} (hN : 3 ≤ N)
    {z : ℂ} (hz : signedFundamentalSector N z)
    (hz0 : canonicalSignedDenominator N z = 0) : |z.im| ≤ signedSectorWidth N := by
  by_cases hy : 0 ≤ z.im
  · rw [abs_of_nonneg hy]
    exact canonicalSignedDenominator_upper_sector_zero_bound hN hz hy hz0
  · have hstar : signedFundamentalSector N (star z) := by
      simpa [signedFundamentalSector] using hz
    have hzero : canonicalSignedDenominator N (star z) = 0 := by
      rw [canonicalSignedDenominator_conj (by omega), hz0, star_zero]
    have hb := canonicalSignedDenominator_upper_sector_zero_bound hN hstar
      (by change 0 ≤ -z.im; linarith) hzero
    simpa [abs_of_neg (lt_of_not_ge hy)] using hb

end
end Komorebi.PaperIV
