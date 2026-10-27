/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.FullZeroSummability
import Mathlib.Analysis.Complex.SummableUniformlyOn

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

def weightedDirichletTerm {ι : Type*} (w : ι → ℕ) (r : ι → ℝ) (i : ι) (s : ℂ) : ℂ :=
  (w i : ℂ) * Complex.exp (-s * (Real.log (r i) : ℂ))

theorem weightedDirichletTerm_norm {ι : Type*} (w : ι → ℕ) (r : ι → ℝ)
    (hr : ∀ i, 0 < r i) (i : ι) (s : ℂ) :
    ‖weightedDirichletTerm w r i s‖ = (w i : ℝ) / r i ^ s.re := by
  rw [weightedDirichletTerm, norm_mul, Complex.norm_natCast, Complex.norm_exp]
  simp only [Complex.mul_re, Complex.neg_re, Complex.neg_im, Complex.ofReal_re,
    Complex.ofReal_im, mul_zero, sub_zero]
  rw [Real.rpow_def_of_pos (hr i), div_eq_mul_inv, ← Real.exp_neg]
  congr 2
  ring

theorem weightedDirichletTerm_differentiable {ι : Type*} (w : ι → ℕ) (r : ι → ℝ) (i : ι) :
    Differentiable ℂ (weightedDirichletTerm w r i) := by
  unfold weightedDirichletTerm
  fun_prop

theorem weightedDirichletTerm_strip_bound {ι : Type*} (w : ι → ℕ) (r : ι → ℝ)
    (hr : ∀ i, 0 < r i) {a b : ℝ} {s : ℂ} (ha : a ≤ s.re) (hb : s.re ≤ b) (i : ι) :
    ‖weightedDirichletTerm w r i s‖ ≤ (w i : ℝ) / r i ^ a + (w i : ℝ) / r i ^ b := by
  rw [weightedDirichletTerm_norm w r hr]
  simp only [Real.rpow_def_of_pos (hr i), div_eq_mul_inv, ← Real.exp_neg]
  have hw := Nat.cast_nonneg (α := ℝ) (w i)
  by_cases hl : 0 ≤ Real.log (r i)
  · have he : Real.exp (-(Real.log (r i) * s.re)) ≤ Real.exp (-(Real.log (r i) * a)) := by
      apply Real.exp_le_exp.mpr
      nlinarith
    exact (mul_le_mul_of_nonneg_left he hw).trans (le_add_of_nonneg_right (by positivity))
  · have he : Real.exp (-(Real.log (r i) * s.re)) ≤ Real.exp (-(Real.log (r i) * b)) := by
      apply Real.exp_le_exp.mpr
      nlinarith
    exact (mul_le_mul_of_nonneg_left he hw).trans (le_add_of_nonneg_left (by positivity))

/-- A direct Weierstrass test on bounded vertical strips. Both sides of the
unit circle are controlled, so small radii require no implicit omission. -/
theorem weightedDirichlet_locally_uniform {ι : Type*} (w : ι → ℕ) (r : ι → ℝ)
    (hr : ∀ i, 0 < r i) (c : ℝ)
    (hs : ∀ t : ℝ, c < t → Summable (fun i => (w i : ℝ) / r i ^ t)) :
    HasSumLocallyUniformlyOn (weightedDirichletTerm w r)
      (fun s => ∑' i, weightedDirichletTerm w r i s) {s : ℂ | c < s.re} := by
  apply hasSumLocallyUniformlyOn_of_of_forall_exists_nhds
  intro s hs0
  change c < s.re at hs0
  let a := (c + s.re) / 2
  let b := s.re + 1
  have ha : c < a := by dsimp [a]; linarith [hs0]
  have hb : c < b := by dsimp [b]; linarith [hs0]
  let U : Set ℂ := {z | a < z.re ∧ z.re < b}
  have hU : IsOpen U := (isOpen_lt continuous_const Complex.continuous_re).inter
    (isOpen_lt Complex.continuous_re continuous_const)
  have hsU : s ∈ U := by constructor <;> dsimp [a, b] <;> linarith [hs0]
  refine ⟨U, mem_nhdsWithin_of_mem_nhds (hU.mem_nhds hsU), ?_⟩
  apply hasSumUniformlyOn_iff_tendstoUniformlyOn.mpr
  apply tendstoUniformlyOn_tsum ((hs a ha).add (hs b hb))
  intro i z hz
  exact weightedDirichletTerm_strip_bound w r hr hz.1.le hz.2.le i

theorem weightedDirichlet_differentiableOn {ι : Type*} (w : ι → ℕ) (r : ι → ℝ)
    (hr : ∀ i, 0 < r i) (c : ℝ)
    (hs : ∀ t : ℝ, c < t → Summable (fun i => (w i : ℝ) / r i ^ t)) :
    DifferentiableOn ℂ (fun s => ∑' i, weightedDirichletTerm w r i s) {s : ℂ | c < s.re} := by
  apply (weightedDirichlet_locally_uniform w r hr c hs).summableLocallyUniformlyOn.differentiableOn
    (isOpen_lt continuous_const Complex.continuous_re)
  intro i s _
  exact weightedDirichletTerm_differentiable w r i s

/-- The exact absolute zero-zeta summand from the manuscript. -/
def absoluteZeroZetaTerm (f : ℂ → ℂ) (z : {z : ℂ // f z = 0}) (s : ℂ) : ℂ :=
  weightedDirichletTerm (fun z : {z : ℂ // f z = 0} => analyticOrderNatAt f z)
    (fun z => ‖(z : ℂ)‖) z s

def absoluteZeroZeta (f : ℂ → ℂ) (s : ℂ) : ℂ := ∑' z, absoluteZeroZetaTerm f z s

theorem zero_norm_pos_of_value_at_zero {f : ℂ → ℂ} (hf : f 0 ≠ 0)
    (z : {z : ℂ // f z = 0}) : 0 < ‖(z : ℂ)‖ := by
  apply norm_pos_iff.mpr
  intro hz
  have h := z.property
  rw [hz] at h
  exact hf h

theorem absoluteZeroZetaTerm_norm {f : ℂ → ℂ} (hf : f 0 ≠ 0)
    (z : {z : ℂ // f z = 0}) (s : ℂ) :
    ‖absoluteZeroZetaTerm f z s‖ = (analyticOrderNatAt f z : ℝ) / ‖(z : ℂ)‖ ^ s.re :=
  weightedDirichletTerm_norm _ _ (zero_norm_pos_of_value_at_zero hf) z s

theorem absoluteZeroZeta_summable_norm_iff {f : ℂ → ℂ} (hf : f 0 ≠ 0) (s : ℂ) :
    Summable (fun z => ‖absoluteZeroZetaTerm f z s‖) ↔ ZeroPowerSummable f s.re := by
  simp only [absoluteZeroZetaTerm_norm hf, ZeroPowerSummable]

theorem absoluteZeroZeta_locally_uniform {f : ℂ → ℂ} (hf : f 0 ≠ 0) (c : ℝ)
    (hs : ∀ t, c < t → ZeroPowerSummable f t) :
    HasSumLocallyUniformlyOn (absoluteZeroZetaTerm f) (absoluteZeroZeta f)
      {s : ℂ | c < s.re} :=
  weightedDirichlet_locally_uniform _ _ (zero_norm_pos_of_value_at_zero hf) c hs

theorem absoluteZeroZeta_differentiableOn {f : ℂ → ℂ} (hf : f 0 ≠ 0) (c : ℝ)
    (hs : ∀ t, c < t → ZeroPowerSummable f t) :
    DifferentiableOn ℂ (absoluteZeroZeta f) {s : ℂ | c < s.re} :=
  weightedDirichlet_differentiableOn _ _ (zero_norm_pos_of_value_at_zero hf) c hs

/-- Exact absolute abscissa, including divergence on and to the left of the boundary. -/
theorem canonicalSignedDenominator_zeta_absolute_convergence {N : ℕ} (hN : 2 ≤ N) (s : ℂ) :
    Summable (fun z => ‖absoluteZeroZetaTerm (canonicalSignedDenominator N) z s‖) ↔ 1 < s.re := by
  rw [absoluteZeroZeta_summable_norm_iff (by rw [canonicalSignedDenominator_zero (by omega)]; exact one_ne_zero)]
  exact canonicalSignedDenominator_zero_power_summable_iff hN s.re

theorem canonicalSignedDenominator_zeta_locally_uniform {N : ℕ} (hN : 2 ≤ N) :
    HasSumLocallyUniformlyOn (absoluteZeroZetaTerm (canonicalSignedDenominator N))
      (absoluteZeroZeta (canonicalSignedDenominator N)) {s : ℂ | 1 < s.re} := by
  apply absoluteZeroZeta_locally_uniform (by rw [canonicalSignedDenominator_zero (by omega)]; exact one_ne_zero)
  intro t ht
  exact (canonicalSignedDenominator_zero_power_summable_iff hN t).mpr ht

theorem canonicalSignedDenominator_zeta_holomorphic {N : ℕ} (hN : 2 ≤ N) :
    DifferentiableOn ℂ (absoluteZeroZeta (canonicalSignedDenominator N)) {s : ℂ | 1 < s.re} := by
  apply absoluteZeroZeta_differentiableOn (by rw [canonicalSignedDenominator_zero (by omega)]; exact one_ne_zero)
  intro t ht
  exact (canonicalSignedDenominator_zero_power_summable_iff hN t).mpr ht

theorem entireReducedDenominator_zeta_absolute_convergence {N : ℕ} (hN : 2 ≤ N) (s : ℂ) :
    Summable (fun z => ‖absoluteZeroZetaTerm (entireReducedDenominator N) z s‖) ↔ 1 / (N : ℝ) < s.re := by
  rw [absoluteZeroZeta_summable_norm_iff (by rw [entireReducedDenominator_zero]; exact one_ne_zero)]
  exact entireReducedDenominator_zero_power_summable_iff hN s.re

theorem entireReducedDenominator_zeta_locally_uniform {N : ℕ} (hN : 2 ≤ N) :
    HasSumLocallyUniformlyOn (absoluteZeroZetaTerm (entireReducedDenominator N))
      (absoluteZeroZeta (entireReducedDenominator N)) {s : ℂ | 1 / (N : ℝ) < s.re} := by
  apply absoluteZeroZeta_locally_uniform (by rw [entireReducedDenominator_zero]; exact one_ne_zero)
  intro t ht
  exact (entireReducedDenominator_zero_power_summable_iff hN t).mpr ht

theorem entireReducedDenominator_zeta_holomorphic {N : ℕ} (hN : 2 ≤ N) :
    DifferentiableOn ℂ (absoluteZeroZeta (entireReducedDenominator N)) {s : ℂ | 1 / (N : ℝ) < s.re} := by
  apply absoluteZeroZeta_differentiableOn (by rw [entireReducedDenominator_zero]; exact one_ne_zero)
  intro t ht
  exact (entireReducedDenominator_zero_power_summable_iff hN t).mpr ht

end
end Komorebi.PaperIV
