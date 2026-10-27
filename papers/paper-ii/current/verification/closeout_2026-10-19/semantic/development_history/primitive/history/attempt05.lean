import KomorebiVerification.PaperII.ReleaseRectifiable
import Mathlib.Analysis.Complex.CauchyIntegral
import Mathlib.Analysis.Calculus.ContDiff.RCLike
import Mathlib.Topology.Algebra.MetricSpace.Lipschitz

set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperII.ReleaseCyclePrimitive
open MeasureTheory Set Filter
open scoped Topology BigOperators
open Komorebi.PaperII.ReleaseAnalyticContour

theorem isCompact_trace (Γ : IntegralCycle) : IsCompact Γ.trace := by
  have heq : Γ.trace = ⋃ i : Fin Γ.count, Γ.curve i '' uIcc (0:ℝ) 1 := by
    ext z
    simp [IntegralCycle.trace]
  rw [heq]
  exact isCompact_iUnion fun i ↦ isCompact_uIcc.image_of_continuousOn (Γ.continuousOn_curve i)

/-- The integral primitive of an integrable complex function is absolutely
continuous, obtained from the two real coordinate primitives. -/
theorem ac_complex_primitive {g : ℝ → ℂ} (hg : IntervalIntegrable g volume 0 1) :
    AbsolutelyContinuousOnInterval (fun s : ℝ ↦ ∫ t : ℝ in 0..s, g t) 0 1 := by
  have hr : IntervalIntegrable (fun t ↦ (g t).re) volume 0 1 :=
    ⟨Complex.reCLM.integrable_comp hg.1, Complex.reCLM.integrable_comp hg.2⟩
  have hi : IntervalIntegrable (fun t ↦ (g t).im) volume 0 1 :=
    ⟨Complex.imCLM.integrable_comp hg.1, Complex.imCLM.integrable_comp hg.2⟩
  have har := Complex.ofRealCLM.lipschitzWith.comp_absolutelyContinuousOnInterval
    (hr.absolutelyContinuousOnInterval_intervalIntegral (c := 0) (by simp))
  have hai := Complex.ofRealCLM.lipschitzWith.comp_absolutelyContinuousOnInterval
    (hi.absolutelyContinuousOnInterval_intervalIntegral (c := 0) (by simp))
  apply (har.add (hai.const_smul Complex.I)).congr
  intro s hs
  have hint := hg.mono_set (uIcc_subset_uIcc_left hs)
  have hreal := Complex.reCLM.intervalIntegral_comp_comm hint
  have himag := Complex.imCLM.intervalIntegral_comp_comm hint
  apply Complex.ext <;> simp_all [Function.comp_def, smul_eq_mul]

theorem ac_curve (Γ : IntegralCycle) (i : Fin Γ.count) :
    AbsolutelyContinuousOnInterval (Γ.curve i) 0 1 := by
  have hconst : AbsolutelyContinuousOnInterval (fun _ : ℝ ↦ Γ.base i) 0 1 :=
    (show LipschitzWith 0 (fun _ : ℝ ↦ Γ.base i) from LipschitzWith.const _).lipschitzOnWith.absolutelyContinuousOnInterval
  exact hconst.add (ac_complex_primitive (Γ.velocity_integrable i))

theorem ae_hasDerivAt_curve (Γ : IntegralCycle) (i : Fin Γ.count) :
    ∀ᵐ s : ℝ, s ∈ uIcc (0:ℝ) 1 → HasDerivAt (Γ.curve i) (Γ.velocity i s) s := by
  filter_upwards [(Γ.velocity_integrable i).ae_hasDerivAt_integral] with s hs hmem
  exact (hs hmem 0 left_mem_uIcc).const_add (Γ.base i)

theorem lipschitzOn_trace_of_holomorphic (Γ : IntegralCycle) {U : Set ℂ}
    (hU : IsOpen U) (hΓ : Γ.trace ⊆ U) {F : ℂ → ℂ}
    (hF : DifferentiableOn ℂ F U) : ∃ K, LipschitzOnWith K F Γ.trace := by
  apply LocallyLipschitzOn.exists_lipschitzOnWith_of_compact (isCompact_trace Γ)
  intro z hz
  have hc : ContDiffAt ℂ 1 F z :=
    (hF.contDiffOn hU z (hΓ hz)).contDiffAt (hU.mem_nhds (hΓ hz))
  obtain ⟨K, t, ht, hKt⟩ := hc.exists_lipschitzOnWith
  exact ⟨K, t, mem_nhdsWithin_of_mem_nhds ht, hKt⟩

theorem integral_deriv_curve_eq_sub (Γ : IntegralCycle) {U : Set ℂ}
    (hU : IsOpen U) (hΓ : Γ.trace ⊆ U) {F : ℂ → ℂ}
    (hF : DifferentiableOn ℂ F U) (i : Fin Γ.count) :
    (∫ s : ℝ in (0:ℝ)..1, Γ.velocity i s • deriv F (Γ.curve i s)) =
      F (Γ.curve i 1) - F (Γ.curve i 0) := by
  have hderiv : ContinuousOn (deriv F) Γ.trace :=
    (hF.deriv hU).continuousOn.mono hΓ
  have hint := Γ.integrable_lineIntegrand hderiv i
  obtain ⟨K, hK⟩ := lipschitzOn_trace_of_holomorphic Γ hU hΓ hF
  have hcomp : AbsolutelyContinuousOnInterval (F ∘ Γ.curve i) 0 1 :=
    hK.comp_absolutelyContinuousOnInterval (fun s hs ↦ ⟨i,s,hs,rfl⟩) (ac_curve Γ i)
  let g : ℝ → ℂ := fun s ↦ F (Γ.curve i s) -
    ∫ t : ℝ in 0..s, Γ.velocity i t • deriv F (Γ.curve i t)
  have hg : AbsolutelyContinuousOnInterval g 0 1 :=
    hcomp.sub (ac_complex_primitive hint)
  have hg0 : ∀ᵐ s : ℝ, s ∈ uIcc (0:ℝ) 1 → HasDerivAt g 0 s := by
    filter_upwards [ae_hasDerivAt_curve Γ i, hint.ae_hasDerivAt_integral] with s hs ht hmem
    have hFs := ((hF (Γ.curve i s) (hΓ ⟨i,s,hmem,rfl⟩)).differentiableAt
      (hU.mem_nhds (hΓ ⟨i,s,hmem,rfl⟩))).hasDerivAt
    have hchain := hFs.scomp s (hs hmem)
    convert! hchain.sub (ht hmem 0 left_mem_uIcc) using 1 <;> simp
  obtain ⟨C, hC⟩ := hg.const_of_ae_hasDerivAt_zero hg0
  have ha := hC 0 left_mem_uIcc
  have hb := hC 1 right_mem_uIcc
  dsimp [g] at ha hb
  simp only [intervalIntegral.integral_same, sub_zero] at ha
  rw [← ha] at hb
  apply eq_sub_iff_add_eq.mpr
  simpa only [smul_eq_mul, add_comm] using (sub_eq_iff_eq_add.mp hb).symm

end Komorebi.PaperII.ReleaseCyclePrimitive

namespace Komorebi.PaperII.ReleaseAnalyticContour.IntegralCycle
open Set
open Komorebi.PaperII.ReleaseCyclePrimitive
open scoped BigOperators

/-- A holomorphic derivative integrates to zero over every actual finite
integrable-velocity closed cycle. No C1 condition is imposed on its curves. -/
theorem lineIntegral_deriv_eq_zero (Γ : IntegralCycle) {U : Set ℂ}
    (hU : IsOpen U) (hΓ : Γ.trace ⊆ U) {F : ℂ → ℂ}
    (hF : DifferentiableOn ℂ F U) : Γ.lineIntegral (deriv F) = 0 := by
  unfold lineIntegral
  apply Finset.sum_eq_zero
  intro i hi
  rw [integral_deriv_curve_eq_sub Γ hU hΓ hF i, Γ.curve_one, Γ.curve_zero, sub_self]

end Komorebi.PaperII.ReleaseAnalyticContour.IntegralCycle
