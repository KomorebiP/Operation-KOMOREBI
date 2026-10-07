/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroZetaConvergence

namespace Komorebi.PaperIV
noncomputable section
open Set Filter Metric
open scoped Topology

def branchedDirichletTerm {ι : Type*} (c L : ι → ℂ) (i : ι) (s : ℂ) : ℂ :=
  c i * Complex.exp (-s * L i)

theorem branchedDirichletTerm_differentiable {ι : Type*} (c L : ι → ℂ) (i : ι) :
    Differentiable ℂ (branchedDirichletTerm c L i) := by
  unfold branchedDirichletTerm
  fun_prop

theorem branchedDirichletTerm_norm {ι : Type*} (c L : ι → ℂ) (r : ι → ℝ)
    (hr : ∀ i, 0 < r i) (hL : ∀ i, (L i).re = Real.log (r i)) (i : ι) (s : ℂ) :
    ‖branchedDirichletTerm c L i s‖ =
      ‖c i‖ / r i ^ s.re * Real.exp (s.im * (L i).im) := by
  rw [branchedDirichletTerm, norm_mul, Complex.norm_exp]
  simp only [Complex.mul_re, Complex.neg_re, Complex.neg_im, hL]
  rw [neg_mul s.im, sub_neg_eq_add, Real.exp_add, Real.rpow_def_of_pos (hr i),
    div_eq_mul_inv, ← Real.exp_neg]
  ring_nf

theorem branchedDirichletTerm_strip_bound {ι : Type*} (c L : ι → ℂ) (r : ι → ℝ)
    (hr : ∀ i, 0 < r i) (hL : ∀ i, (L i).re = Real.log (r i))
    {B K a b : ℝ} (_hB : 0 ≤ B) (hK : 0 ≤ K) (harg : ∀ i, |(L i).im| ≤ B)
    {s : ℂ} (ha : a ≤ s.re) (hb : s.re ≤ b) (hi : |s.im| ≤ K) (i : ι) :
    ‖branchedDirichletTerm c L i s‖ ≤
      Real.exp (K * B) * (‖c i‖ / r i ^ a + ‖c i‖ / r i ^ b) := by
  rw [branchedDirichletTerm_norm c L r hr hL]
  have hs : ‖c i‖ / r i ^ s.re ≤ ‖c i‖ / r i ^ a + ‖c i‖ / r i ^ b := by
    have h := weightedDirichletTerm_strip_bound (fun _ : ι => 1) r hr ha hb i
    rw [weightedDirichletTerm_norm _ _ hr] at h
    norm_num only [Nat.cast_one] at h
    have h' := mul_le_mul_of_nonneg_left h (norm_nonneg (c i))
    simpa only [mul_add, mul_one_div] using h'
  have he : Real.exp (s.im * (L i).im) ≤ Real.exp (K * B) := by
    apply Real.exp_le_exp.mpr
    calc _ ≤ |s.im * (L i).im| := le_abs_self _
         _ = |s.im| * |(L i).im| := abs_mul _ _
         _ ≤ K * B := mul_le_mul hi (harg i) (abs_nonneg _) hK
  calc
    _ ≤ (‖c i‖ / r i ^ a + ‖c i‖ / r i ^ b) * Real.exp (K * B) :=
      mul_le_mul hs he (Real.exp_nonneg _) (add_nonneg (div_nonneg (norm_nonneg _) (Real.rpow_nonneg (hr i).le _))
        (div_nonneg (norm_nonneg _) (Real.rpow_nonneg (hr i).le _)))
    _ = _ := mul_comm _ _

/-- Absolute convergence at an individual complex parameter. -/
theorem branchedDirichlet_summable_norm {ι : Type*} (c L : ι → ℂ) (r : ι → ℝ)
    (hr : ∀ i, 0 < r i) (hL : ∀ i, (L i).re = Real.log (r i))
    {B : ℝ} (hB : 0 ≤ B) (harg : ∀ i, |(L i).im| ≤ B) (s : ℂ)
    (hs : Summable (fun i => ‖c i‖ / r i ^ s.re)) :
    Summable (fun i => ‖branchedDirichletTerm c L i s‖) := by
  apply ((hs.add hs).mul_left (Real.exp (|s.im| * B))).of_norm_bounded
  intro i
  rw [norm_norm]
  exact branchedDirichletTerm_strip_bound c L r hr hL hB (abs_nonneg _) harg le_rfl le_rfl le_rfl i

/-- A local Weierstrass theorem for bounded choices of logarithmic arguments.
It retains all finite exceptional terms and does not require a global branch. -/
theorem branchedDirichlet_locally_uniform {ι : Type*} (c L : ι → ℂ) (r : ι → ℝ)
    (hr : ∀ i, 0 < r i) (hL : ∀ i, (L i).re = Real.log (r i))
    {B : ℝ} (hB : 0 ≤ B) (harg : ∀ i, |(L i).im| ≤ B) (U : Set ℂ)
    (hs : ∀ s ∈ U, ∃ a b : ℝ, a < s.re ∧ s.re < b ∧
      Summable (fun i => ‖c i‖ / r i ^ a) ∧ Summable (fun i => ‖c i‖ / r i ^ b)) :
    HasSumLocallyUniformlyOn (branchedDirichletTerm c L)
      (fun s => ∑' i, branchedDirichletTerm c L i s) U := by
  apply hasSumLocallyUniformlyOn_of_of_forall_exists_nhds
  intro s hsU
  obtain ⟨a, b, ha, hb, hsa, hsb⟩ := hs s hsU
  let V := {z : ℂ | a < z.re ∧ z.re < b ∧ |z.im| < |s.im| + 1}
  have hV : IsOpen V := (isOpen_lt continuous_const Complex.continuous_re).inter
    ((isOpen_lt Complex.continuous_re continuous_const).inter
      (isOpen_lt Complex.continuous_im.abs continuous_const))
  have hsV : s ∈ V := ⟨ha, hb, by linarith⟩
  refine ⟨V, mem_nhdsWithin_of_mem_nhds (hV.mem_nhds hsV), ?_⟩
  apply hasSumUniformlyOn_iff_tendstoUniformlyOn.mpr
  apply tendstoUniformlyOn_tsum ((hsa.add hsb).mul_left (Real.exp ((|s.im| + 1) * B)))
  intro i z hz
  exact branchedDirichletTerm_strip_bound c L r hr hL hB (by positivity) harg hz.1.le hz.2.1.le hz.2.2.le i

theorem branchedDirichlet_entire {ι : Type*} (c L : ι → ℂ) (r : ι → ℝ)
    (hr : ∀ i, 0 < r i) (hL : ∀ i, (L i).re = Real.log (r i))
    {B : ℝ} (hB : 0 ≤ B) (harg : ∀ i, |(L i).im| ≤ B)
    (hs : ∀ t : ℝ, Summable (fun i => ‖c i‖ / r i ^ t)) :
    HasSumLocallyUniformlyOn (branchedDirichletTerm c L)
      (fun s => ∑' i, branchedDirichletTerm c L i s) univ ∧
    Differentiable ℂ (fun s => ∑' i, branchedDirichletTerm c L i s) := by
  have h := branchedDirichlet_locally_uniform c L r hr hL hB harg univ
    (fun s _ => ⟨s.re - 1, s.re + 1, by linarith, by linarith, hs _, hs _⟩)
  refine ⟨h, differentiableOn_univ.mp ?_⟩
  exact h.summableLocallyUniformlyOn.differentiableOn isOpen_univ
    (fun i s _ => branchedDirichletTerm_differentiable c L i s)

theorem branchedDirichlet_halfplane {ι : Type*} (c L : ι → ℂ) (r : ι → ℝ)
    (hr : ∀ i, 0 < r i) (hL : ∀ i, (L i).re = Real.log (r i))
    {B : ℝ} (hB : 0 ≤ B) (harg : ∀ i, |(L i).im| ≤ B) (σ : ℝ)
    (hs : ∀ t : ℝ, σ < t → Summable (fun i => ‖c i‖ / r i ^ t)) :
    HasSumLocallyUniformlyOn (branchedDirichletTerm c L)
      (fun s => ∑' i, branchedDirichletTerm c L i s) {s : ℂ | σ < s.re} ∧
    DifferentiableOn ℂ (fun s => ∑' i, branchedDirichletTerm c L i s) {s : ℂ | σ < s.re} := by
  have h := branchedDirichlet_locally_uniform c L r hr hL hB harg {s : ℂ | σ < s.re}
    (fun s hs0 => ⟨(σ + s.re) / 2, s.re + 1, by dsimp at hs0; linarith,
      by linarith, hs _ (by dsimp at hs0; linarith), hs _ (by dsimp at hs0; linarith)⟩)
  exact ⟨h, h.summableLocallyUniformlyOn.differentiableOn
    (isOpen_lt continuous_const Complex.continuous_re)
    (fun i s _ => branchedDirichletTerm_differentiable c L i s)⟩

end
end Komorebi.PaperIV
