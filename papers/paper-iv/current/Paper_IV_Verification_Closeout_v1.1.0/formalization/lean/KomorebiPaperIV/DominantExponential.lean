/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SignedSectorConfinement
import Mathlib.Analysis.SpecialFunctions.Pow.Asymptotics

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

/-- A finite collection of strictly positive gaps has a common positive bound. -/
theorem finite_positive_gap {s : Finset ℕ} {d : ℕ → ℝ}
    (hd : ∀ i ∈ s, 0 < d i) : ∃ δ : ℝ, 0 < δ ∧ ∀ i ∈ s, δ ≤ d i := by
  by_cases hs : s.Nonempty
  · exact ⟨s.inf' hs d, (Finset.lt_inf'_iff hs).mpr hd, fun i hi => s.inf'_le d hi⟩
  · exact ⟨1, by norm_num, by simp [Finset.not_nonempty_iff_eq_empty.mp hs]⟩

/-- Quantitative one-term dominance of an actual finite exponential sum. -/
theorem finite_exponential_dominant_bound {s : Finset ℕ} {a : ℕ → ℂ}
    {k : ℕ} (hk : k ∈ s) {u : ℂ} {δ r : ℝ} (hr : 0 ≤ r)
    (hgap : ∀ i ∈ s.erase k, ((a i - a k) * u).re ≤ -δ) :
    ‖Complex.exp (-(a k * ((r : ℂ) * u))) *
      (∑ i ∈ s, Complex.exp (a i * ((r : ℂ) * u))) - 1‖ ≤
      ((s.erase k).card : ℝ) * Real.exp (-δ * r) := by
  rw [finite_one_term_normalization hk, add_sub_cancel_left]
  calc
    _ ≤ ∑ i ∈ s.erase k, ‖Complex.exp ((a i - a k) * ((r : ℂ) * u))‖ := norm_sum_le _ _
    _ ≤ ∑ _i ∈ s.erase k, Real.exp (-δ * r) := by
      apply Finset.sum_le_sum
      intro i hi
      rw [Complex.norm_exp]
      apply Real.exp_le_exp.mpr
      have he : ((a i - a k) * ((r : ℂ) * u)).re = ((a i - a k) * u).re * r := by
        rw [show (a i - a k) * ((r : ℂ) * u) = ((a i - a k) * u) * (r : ℂ) by ring,
          Complex.mul_re]
        simp
      rw [he]
      exact mul_le_mul_of_nonneg_right (hgap i hi) hr
    _ = _ := by simp

theorem finite_exponential_dominant_tendsto {s : Finset ℕ} {a : ℕ → ℂ}
    {k : ℕ} (hk : k ∈ s) {u : ℂ}
    (hgap : ∀ i ∈ s.erase k, (a i * u).re < (a k * u).re) :
    Tendsto (fun r : ℝ => Complex.exp (-(a k * ((r : ℂ) * u))) *
      (∑ i ∈ s, Complex.exp (a i * ((r : ℂ) * u)))) atTop (𝓝 1) := by
  obtain ⟨δ, hδ, hδgap⟩ := finite_positive_gap (fun i hi => sub_pos.mpr (hgap i hi))
  have ht : Tendsto (fun r : ℝ => ((s.erase k).card : ℝ) * Real.exp (-δ * r)) atTop (𝓝 0) := by
    simpa only [mul_zero, neg_mul, Function.comp_apply, id_eq] using
      (Real.tendsto_exp_neg_atTop_nhds_zero.comp (tendsto_id.const_mul_atTop hδ)).const_mul ((s.erase k).card : ℝ)
  apply tendsto_iff_norm_sub_tendsto_zero.mpr
  apply squeeze_zero' (Eventually.of_forall (fun _ => norm_nonneg _)) _ ht
  filter_upwards [eventually_ge_atTop (0 : ℝ)] with r hr
  exact finite_exponential_dominant_bound hk hr (fun i hi => by
    rw [sub_mul, Complex.sub_re]; linarith [hδgap i hi])

/-- A unit complex number has real part strictly below one unless it is one. -/
theorem unit_complex_re_lt_one {a : ℂ} (ha : ‖a‖ = 1) (h : a ≠ 1) : a.re < 1 := by
  have he := Complex.re_le_norm a
  rw [ha] at he
  apply lt_of_le_of_ne he
  intro hr
  have hi : a.im = 0 := by
    have hs := Complex.sq_norm_sub_sq_re a
    rw [ha, hr] at hs
    nlinarith [sq_nonneg a.im]
  apply h
  exact Complex.ext hr (by simpa using hi)

theorem canonicalSignedVertex_injective {N : ℕ} (hN : 0 < N) :
    Set.InjOn (canonicalSignedVertex N) (↑(Finset.range N) : Set ℕ) := by
  intro i hi j hj he
  apply (canonicalPrimitiveRoot_isPrimitive hN).pow_inj
    (Finset.mem_range.mp hi) (Finset.mem_range.mp hj)
  exact mul_left_cancel₀ (by rw [← norm_ne_zero_iff, norm_signedRoot hN (canonicalSignedRoot_pow hN)]; exact one_ne_zero) he

theorem canonicalSignedVertex_mul_star_self (N k : ℕ) :
    canonicalSignedVertex N k * star (canonicalSignedVertex N k) = 1 := by
  rw [Complex.star_def, Complex.mul_conj, Complex.normSq_eq_norm_sq, norm_canonicalSignedVertex]
  norm_num

/-- Looking straight toward any polygon vertex gives a strictly dominant term. -/
theorem canonicalSignedDenominator_dominant_ray {N : ℕ} (hN : 0 < N)
    {k : ℕ} (hk : k < N) :
    Tendsto (fun r : ℝ => (N : ℂ) * Complex.exp (-(r : ℂ)) *
      canonicalSignedDenominator N ((r : ℂ) * star (canonicalSignedVertex N k))) atTop (𝓝 1) := by
  have h := finite_exponential_dominant_tendsto (a := canonicalSignedVertex N)
    (Finset.mem_range.mpr hk) (u := star (canonicalSignedVertex N k)) (fun i hi => ?_)
  · convert! h using 1
    funext r
    rw [show canonicalSignedVertex N k * ((r : ℂ) * star (canonicalSignedVertex N k)) = (r : ℂ) by
      rw [mul_left_comm, canonicalSignedVertex_mul_star_self, mul_one]]
    unfold canonicalSignedDenominator
    rw [entireSigned_zero_eq_average]
    have hn : (N : ℂ) ≠ 0 := by exact_mod_cast hN.ne'
    dsimp [canonicalSignedVertex]
    field_simp
    apply Finset.sum_congr rfl
    intro i _
    congr 1
    ring
  · rw [canonicalSignedVertex_mul_star_self]
    apply unit_complex_re_lt_one (by simp [norm_canonicalSignedVertex])
    intro he
    have hij := mul_right_cancel₀
      (show star (canonicalSignedVertex N k) ≠ 0 by rw [← norm_ne_zero_iff]; simp [norm_canonicalSignedVertex])
      (he.trans (canonicalSignedVertex_mul_star_self N k).symm)
    exact (Finset.mem_erase.mp hi).1 (canonicalSignedVertex_injective hN
      (Finset.mem_erase.mp hi).2 (Finset.mem_range.mpr hk) hij)

end
end Komorebi.PaperIV
