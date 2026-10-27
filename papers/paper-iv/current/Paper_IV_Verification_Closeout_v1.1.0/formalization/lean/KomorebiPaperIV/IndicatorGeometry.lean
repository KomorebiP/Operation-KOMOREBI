/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.DominantExponential
import Mathlib.Topology.Order.Lattice

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

def rayDirection (θ : ℝ) : ℂ := Complex.exp ((θ : ℂ) * Complex.I)

theorem norm_rayDirection (θ : ℝ) : ‖rayDirection θ‖ = 1 :=
  Complex.norm_exp_ofReal_mul_I θ

def signedProjection (N : ℕ) (θ : ℝ) (k : ℕ) : ℝ :=
  (canonicalSignedVertex N k * rayDirection θ).re

def signedIndicator (N : ℕ) (hN : 0 < N) (θ : ℝ) : ℝ :=
  (Finset.range N).sup' ⟨0, Finset.mem_range.mpr hN⟩ (signedProjection N θ)

theorem signedProjection_cos (N k : ℕ) (θ : ℝ) :
    signedProjection N θ k = Real.cos (θ + (2 * k + 1) * (Real.pi / N)) := by
  unfold signedProjection rayDirection
  rw [canonicalSignedVertex_exp, ← Complex.exp_add]
  have he : (((2 * (k : ℝ) + 1) * (Real.pi / N) : ℝ) : ℂ) * Complex.I + (θ : ℂ) * Complex.I =
      ((θ + (2 * k + 1) * (Real.pi / N) : ℝ) : ℂ) * Complex.I := by push_cast; ring
  rw [he, Complex.exp_ofReal_mul_I_re]

theorem signedIndicator_cos (N : ℕ) (hN : 0 < N) (θ : ℝ) :
    signedIndicator N hN θ = (Finset.range N).sup' ⟨0, Finset.mem_range.mpr hN⟩
      (fun k => Real.cos (θ + (2 * k + 1) * (Real.pi / N))) := by
  unfold signedIndicator
  congr 1
  funext k
  exact signedProjection_cos N k θ

theorem continuous_signedProjection (N k : ℕ) : Continuous (fun θ => signedProjection N θ k) := by
  simp only [signedProjection_cos]
  fun_prop

theorem continuous_signedIndicator (N : ℕ) (hN : 0 < N) : Continuous (signedIndicator N hN) :=
  Continuous.finset_sup'_apply _ (fun k _ => continuous_signedProjection N k)

theorem signedProjection_le_indicator {N k : ℕ} (hN : 0 < N) (hk : k < N) (θ : ℝ) :
    signedProjection N θ k ≤ signedIndicator N hN θ :=
  (Finset.range N).le_sup' _ (Finset.mem_range.mpr hk)

theorem canonicalSignedVertex_sum_zero {N : ℕ} (hN : 2 ≤ N) :
    ∑ k ∈ Finset.range N, canonicalSignedVertex N k = 0 := by
  simp only [canonicalSignedVertex, ← Finset.mul_sum,
    (canonicalPrimitiveRoot_isPrimitive (show 0 < N by omega)).geom_sum_eq_zero (show 1 < N by omega), mul_zero]

theorem signedIndicator_nonneg {N : ℕ} (hN : 2 ≤ N) (θ : ℝ) :
    0 ≤ signedIndicator N (by omega) θ := by
  have he : (∑ k ∈ Finset.range N, signedProjection N θ k) = 0 := by
    simp only [signedProjection, ← Complex.re_sum, ← Finset.sum_mul, canonicalSignedVertex_sum_zero hN, zero_mul, Complex.zero_re]
  have hb := Finset.sum_le_sum (fun k hk => signedProjection_le_indicator (show 0 < N by omega) (Finset.mem_range.mp hk) θ)
  rw [he] at hb
  simp only [Finset.sum_const, Finset.card_range, nsmul_eq_mul] at hb
  exact nonneg_of_mul_nonneg_right hb (by exact_mod_cast (show 0 < N by omega))

theorem canonicalSignedVertex_pow {N : ℕ} (hN : 0 < N) (k : ℕ) :
    canonicalSignedVertex N k ^ N = -1 := by
  simp only [canonicalSignedVertex, mul_pow, pow_right_comm (canonicalPrimitiveRoot N) k N,
    canonicalSignedRoot_pow hN, (canonicalPrimitiveRoot_isPrimitive hN).pow_eq_one, one_pow, mul_one]

theorem signed_root_in_vertices {N : ℕ} (hN : 0 < N) {a : ℂ} (ha : a ^ N = -1) :
    ∃ k < N, canonicalSignedVertex N k = a := by
  have : NeZero N := ⟨hN.ne'⟩
  have hρ : canonicalSignedRoot N ≠ 0 := by
    rw [← norm_ne_zero_iff, norm_signedRoot hN (canonicalSignedRoot_pow hN)]; exact one_ne_zero
  have hp : (a / canonicalSignedRoot N) ^ N = 1 := by
    rw [div_pow, ha, canonicalSignedRoot_pow hN]; norm_num
  obtain ⟨k, hk, he⟩ := (canonicalPrimitiveRoot_isPrimitive hN).eq_pow_of_pow_eq_one hp
  refine ⟨k, hk, ?_⟩
  rw [canonicalSignedVertex, he]
  field_simp

/-- Two points on the unit circle with equal real parts are equal or conjugate. -/
theorem unit_complex_same_real {a b : ℂ} (ha : ‖a‖ = 1) (hb : ‖b‖ = 1)
    (hr : a.re = b.re) : a = b ∨ a = star b := by
  have hsa := Complex.sq_norm_sub_sq_re a
  have hsb := Complex.sq_norm_sub_sq_re b
  rw [ha, hr] at hsa
  rw [hb] at hsb
  have he : (a.im - b.im) * (a.im + b.im) = 0 := by nlinarith
  rcases mul_eq_zero.mp he with hm | hp
  · exact Or.inl (Complex.ext hr (sub_eq_zero.mp hm))
  · exact Or.inr (Complex.ext (by simpa using hr) (by simp only [Complex.star_def, Complex.conj_im]; linarith))

/-- A tie between maximal projections is possible only on an Nth-root ray. -/
theorem signed_maximizer_strict_of_not_tie {N k : ℕ} (hN : 0 < N) {u : ℂ}
    (hu : ‖u‖ = 1) (hnt : u ^ N ≠ 1) (hk : k < N)
    (hmax : ∀ j < N, (canonicalSignedVertex N j * u).re ≤ (canonicalSignedVertex N k * u).re)
    {l : ℕ} (hl : l < N) (hlk : l ≠ k) :
    (canonicalSignedVertex N l * u).re < (canonicalSignedVertex N k * u).re := by
  have hun : u ≠ 0 := by rw [← norm_ne_zero_iff, hu]; exact one_ne_zero
  have hneq : canonicalSignedVertex N l * u ≠ canonicalSignedVertex N k * u := by
    intro he
    exact hlk (canonicalSignedVertex_injective hN (Finset.mem_range.mpr hl) (Finset.mem_range.mpr hk) (mul_right_cancel₀ hun he))
  apply lt_of_le_of_ne (hmax l hl)
  intro he
  have hconj := (unit_complex_same_real (by simp [norm_canonicalSignedVertex, hu])
    (by simp [norm_canonicalSignedVertex, hu]) he).resolve_left hneq
  have hab : (canonicalSignedVertex N l * u) * (canonicalSignedVertex N k * u) = 1 := by
    rw [hconj, mul_comm, Complex.star_def, Complex.mul_conj, Complex.normSq_eq_norm_sq]
    simp [norm_canonicalSignedVertex, hu]
  have hp := congrArg (fun z : ℂ => z ^ N) hab
  simp only [mul_pow, canonicalSignedVertex_pow hN, one_pow] at hp
  have hsq : (u ^ N) ^ 2 = 1 := by linear_combination hp
  have hminus : u ^ N = -1 := (sq_eq_one_iff.mp hsq).resolve_left hnt
  obtain ⟨j, hj, hju⟩ := signed_root_in_vertices hN (a := u⁻¹) (by rw [inv_pow, hminus]; norm_num)
  have hjone : canonicalSignedVertex N j * u = 1 := by rw [hju, inv_mul_cancel₀ hun]
  have hkone : canonicalSignedVertex N k * u = 1 := by
    by_contra hn
    have ht := unit_complex_re_lt_one (by simp [norm_canonicalSignedVertex, hu]) hn
    have hh := hmax j hj
    rw [hjone] at hh
    exact (not_lt_of_ge hh) ht
  have hlone : canonicalSignedVertex N l * u = 1 := by
    by_contra hn
    have ht := unit_complex_re_lt_one (by simp [norm_canonicalSignedVertex, hu]) hn
    rw [he, hkone] at ht
    exact lt_irrefl _ ht
  exact hneq (hlone.trans hkone.symm)

/-- Tie directions, including all periods, in the manuscript's normalization. -/
def signedTieDirection (N : ℕ) (θ : ℝ) : Prop :=
  ∃ k : ℤ, θ = 2 * Real.pi * k / N

theorem signedTieDirection_iff {N : ℕ} (hN : 0 < N) (θ : ℝ) :
    signedTieDirection N θ ↔ rayDirection θ ^ N = 1 := by
  rw [rayDirection, ← Complex.exp_nat_mul, Complex.exp_eq_one_iff]
  constructor
  · rintro ⟨k, rfl⟩
    refine ⟨k, ?_⟩
    have hn : (N : ℂ) ≠ 0 := by exact_mod_cast hN.ne'
    push_cast
    field_simp
  · rintro ⟨k, hk⟩
    refine ⟨k, ?_⟩
    have he := congrArg Complex.im hk
    simp only [Complex.mul_im, Complex.mul_re, Complex.natCast_re, Complex.natCast_im,
      Complex.intCast_re, Complex.intCast_im, Complex.ofReal_re, Complex.ofReal_im,
      Complex.I_im, Complex.I_re] at he
    have hn : (N : ℝ) ≠ 0 := by exact_mod_cast hN.ne'
    apply (eq_div_iff hn).mpr
    norm_num at he
    linear_combination he

end
end Komorebi.PaperIV
