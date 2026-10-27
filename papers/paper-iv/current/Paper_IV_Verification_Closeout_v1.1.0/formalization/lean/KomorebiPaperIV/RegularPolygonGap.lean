/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ExponentialRemainder

/-! # The canonical polygon gap and actual signed-remainder bounds -/

namespace Komorebi.PaperIV
noncomputable section

def canonicalSignedVertex (N l : ℕ) : ℂ :=
  canonicalSignedRoot N * canonicalPrimitiveRoot N ^ l

def signedPolygonGap (N : ℕ) : ℝ :=
  Real.cos (Real.pi / N) - Real.cos (3 * (Real.pi / N))

theorem canonicalSignedVertex_exp (N l : ℕ) :
    canonicalSignedVertex N l =
      Complex.exp ((((2 * (l : ℝ) + 1) * (Real.pi / N) : ℝ) : ℂ) * Complex.I) := by
  unfold canonicalSignedVertex canonicalSignedRoot canonicalPrimitiveRoot
  rw [← Complex.exp_nat_mul, ← Complex.exp_add]
  congr 1
  push_cast
  ring

theorem canonicalSignedVertex_re (N l : ℕ) :
    (canonicalSignedVertex N l).re = Real.cos ((2 * l + 1) * (Real.pi / N)) := by
  rw [canonicalSignedVertex_exp, Complex.exp_ofReal_mul_I_re]

theorem canonicalSignedVertex_im (N l : ℕ) :
    (canonicalSignedVertex N l).im = Real.sin ((2 * l + 1) * (Real.pi / N)) := by
  rw [canonicalSignedVertex_exp, Complex.exp_ofReal_mul_I_im]

theorem norm_canonicalSignedVertex (N l : ℕ) : ‖canonicalSignedVertex N l‖ = 1 := by
  rw [canonicalSignedVertex_exp, Complex.norm_exp]
  simp

theorem canonicalSignedVertex_last_angle {N : ℕ} (hN : 0 < N) :
    (2 * ((N - 1 : ℕ) : ℝ) + 1) * (Real.pi / N) =
      2 * Real.pi - Real.pi / N := by
  rw [Nat.cast_sub (by omega : 1 ≤ N)]
  have hn : (N : ℝ) ≠ 0 := by exact_mod_cast hN.ne'
  push_cast
  field_simp
  ring

theorem canonicalSignedVertex_last_re {N : ℕ} (hN : 0 < N) :
    (canonicalSignedVertex N (N - 1)).re = Real.cos (Real.pi / N) := by
  rw [canonicalSignedVertex_re, canonicalSignedVertex_last_angle hN, Real.cos_two_pi_sub]

theorem canonicalSignedVertex_last_im {N : ℕ} (hN : 0 < N) :
    (canonicalSignedVertex N (N - 1)).im = -Real.sin (Real.pi / N) := by
  rw [canonicalSignedVertex_im, canonicalSignedVertex_last_angle hN, Real.sin_two_pi_sub]

theorem signedPolygonGap_pos {N : ℕ} (hN : 3 ≤ N) : 0 < signedPolygonGap N := by
  have hn : (3 : ℝ) ≤ N := by exact_mod_cast hN
  have hp : 0 < Real.pi / N := div_pos Real.pi_pos (by linarith)
  have he : Real.pi / N * N = Real.pi := div_mul_cancel₀ _ (by linarith)
  have h3 : 3 * (Real.pi / N) ≤ Real.pi := by nlinarith
  exact sub_pos.mpr (Real.cos_lt_cos_of_nonneg_of_le_pi hp.le h3 (by linarith))

/-- Every nonadjacent vertex has the precise positive real-part gap. -/
theorem canonicalSignedVertex_re_gap {N l : ℕ} (hN : 3 ≤ N)
    (hl : l ∈ ((Finset.range N).erase 0).erase (N - 1)) :
    (canonicalSignedVertex N l - canonicalSignedVertex N (N - 1)).re ≤
      -signedPolygonGap N := by
  have hi : 1 ≤ l ∧ l ≤ N - 2 := by
    simp only [Finset.mem_erase, Finset.mem_range] at hl
    omega
  have hn : (3 : ℝ) ≤ N := by exact_mod_cast hN
  have hl1 : (1 : ℝ) ≤ l := by exact_mod_cast hi.1
  have hl2 : (l : ℝ) ≤ N - 2 := by
    have hh : (l : ℝ) + 2 ≤ N := by exact_mod_cast (show l + 2 ≤ N by omega)
    linarith
  let α : ℝ := Real.pi / N
  let θ : ℝ := (2 * l + 1) * α
  have hp : 0 < α := div_pos Real.pi_pos (by linarith)
  have he : α * N = Real.pi := div_mul_cancel₀ _ (by linarith)
  have hlo : 3 * α ≤ θ := by dsimp [θ]; nlinarith
  have hhi : θ ≤ 2 * Real.pi - 3 * α := by dsimp [θ]; nlinarith
  have hc : Real.cos θ ≤ Real.cos (3 * α) := by
    by_cases hθ : θ ≤ Real.pi
    · exact Real.cos_le_cos_of_nonneg_of_le_pi (by positivity) hθ hlo
    · have hc := Real.cos_le_cos_of_nonneg_of_le_pi
        (by positivity : 0 ≤ 3 * α) (by linarith : 2 * Real.pi - θ ≤ Real.pi)
        (by linarith : 3 * α ≤ 2 * Real.pi - θ)
      simpa [Real.cos_two_pi_sub] using hc
  rw [Complex.sub_re, canonicalSignedVertex_re, canonicalSignedVertex_last_re (by omega)]
  unfold signedPolygonGap
  change Real.cos θ - Real.cos α ≤ -(Real.cos α - Real.cos (3 * α))
  linarith

/-- The actual remainder satisfies the paper's exponential bound for every q. -/
theorem canonicalSignedRemainder_strip_bound {N : ℕ} (hN : 3 ≤ N)
    {Y : ℝ} {z : ℂ} (hx : 0 ≤ z.re) (hy : |z.im| ≤ Y) (q : ℕ) :
    ‖signedExponentialRemainder N (canonicalPrimitiveRoot N) (canonicalSignedRoot N) q z‖ ≤
      ((N - 2 : ℕ) : ℝ) * 2 ^ q *
        Real.exp (-signedPolygonGap N * z.re + 2 * Y) := by
  have hnorm (l : ℕ) : ‖canonicalSignedVertex N l - canonicalSignedVertex N (N - 1)‖ ≤ 2 := by
    calc _ ≤ ‖canonicalSignedVertex N l‖ + ‖canonicalSignedVertex N (N - 1)‖ := norm_sub_le _ _
         _ = 2 := by rw [norm_canonicalSignedVertex, norm_canonicalSignedVertex]; norm_num
  have hs : (((Finset.range N).erase 0).erase (N - 1)).card = N - 2 := by
    rw [Finset.card_erase_of_mem, Finset.card_erase_of_mem, Finset.card_range]
    · omega
    · simp; omega
    · simp; omega
  have h := finiteExponentialRemainder_strip_bound (a := canonicalSignedVertex N)
    (b := canonicalSignedVertex N (N - 1)) (by norm_num : (0 : ℝ) ≤ 2) (by norm_num : (0 : ℝ) ≤ 2)
    (fun l hl => canonicalSignedVertex_re_gap hN hl)
    (fun l _ => (Complex.abs_im_le_norm _).trans (hnorm l)) (fun l _ => hnorm l) hx hy q
  rw [hs] at h
  convert h using 1
  rfl

/-- The difference between the adjacent exponents is exactly 2 i sin(pi/N). -/
theorem canonicalSignedVertex_adjacent_difference {N : ℕ} (hN : 0 < N) :
    canonicalSignedRoot N - canonicalSignedVertex N (N - 1) =
      (2 * (Real.sin (Real.pi / N) : ℂ)) * Complex.I := by
  have hzero : canonicalSignedRoot N = canonicalSignedVertex N 0 := by
    simp [canonicalSignedVertex]
  rw [hzero]
  apply Complex.ext
  · simp only [Complex.sub_re, Complex.mul_re, Complex.mul_im, Complex.ofReal_re,
      Complex.ofReal_im, Complex.I_re, Complex.I_im]
    rw [canonicalSignedVertex_last_re hN, canonicalSignedVertex_re]
    norm_num only [Nat.cast_zero, mul_zero, zero_add, one_mul, sub_self, mul_one,
      sub_zero, zero_mul, (show (2 : ℂ).im = 0 from rfl)]
  · simp only [Complex.sub_im, Complex.mul_im, Complex.mul_re, Complex.ofReal_re,
      Complex.ofReal_im, Complex.I_re, Complex.I_im]
    rw [canonicalSignedVertex_last_im hN, canonicalSignedVertex_im]
    norm_num only [Nat.cast_zero, mul_zero, zero_add, one_mul, mul_one, add_zero,
      sub_neg_eq_add, zero_mul, (show (2 : ℂ).re = 2 from rfl)]
    ring

end
end Komorebi.PaperIV
