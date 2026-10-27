import KomorebiVerification.PaperII.ReleaseCycleDixon
import KomorebiVerification.PaperII.ReleaseCycleDSlope
import Mathlib.Analysis.Complex.Liouville

set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.ReleaseCycleCauchy
open Set MeasureTheory Filter
open scoped Topology BigOperators
open Komorebi.PaperII.ReleaseAnalyticContour
open Komorebi.PaperII.ReleaseCycleParameter
open Komorebi.PaperII.ReleaseCycleWinding
open Komorebi.PaperII.ReleaseCycleDixon
open Komorebi.PaperII.ReleaseCycleDSlope

variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
variable [NormedSpace ℝ E] [IsScalarTower ℝ ℂ E] [CompleteSpace E]

/-- Dixon's two-cycle continuation. Taking the difference directly avoids
introducing a separate reversed-cycle representation. -/
def pairDixon (Γ Δ : IntegralCycle) (f : ℂ → E) (U : Set ℂ) (w : ℂ) : E :=
  if w ∈ U then Γ.lineIntegral (dslope f w) - Δ.lineIntegral (dslope f w)
  else dixonH2 Γ f w - dixonH2 Δ f w

theorem differentiable_pairDixon (Γ Δ : IntegralCycle) {f : ℂ → E} {U : Set ℂ}
    (hU : IsOpen U) (hf : DifferentiableOn ℂ f U)
    (hΓ : Γ.trace ⊆ U) (hΔ : Δ.trace ⊆ U)
    (hnull : ∀ w ∉ U, winding Γ w = winding Δ w)
    (hmatch : ∀ w ∈ U, w ∉ Γ.trace → w ∉ Δ.trace →
      winding Γ w = winding Δ w →
      Γ.lineIntegral (dslope f w) - Δ.lineIntegral (dslope f w) =
        dixonH2 Γ f w - dixonH2 Δ f w) :
    Differentiable ℂ (pairDixon Γ Δ f U) := by
  intro w
  by_cases hw : w ∈ U
  · have hd := ((differentiableOn_lineIntegral_dslope Γ hU hf hΓ w hw).differentiableAt
        (hU.mem_nhds hw)).sub
        ((differentiableOn_lineIntegral_dslope Δ hU hf hΔ w hw).differentiableAt
        (hU.mem_nhds hw))
    apply hd.congr_of_eventuallyEq
    filter_upwards [hU.mem_nhds hw] with a ha
    simp only [pairDixon, if_pos ha]
  · have hwΓ : w ∉ Γ.trace := fun hz ↦ hw (hΓ hz)
    have hwΔ : w ∉ Δ.trace := fun hz ↦ hw (hΔ hz)
    have hcompΓ : ContinuousOn f Γ.trace := hf.continuousOn.mono hΓ
    have hcompΔ : ContinuousOn f Δ.trace := hf.continuousOn.mono hΔ
    have hd := (hasDerivAt_dixonH2 Γ hcompΓ hwΓ).differentiableAt.sub
      (hasDerivAt_dixonH2 Δ hcompΔ hwΔ).differentiableAt
    apply hd.congr_of_eventuallyEq
    filter_upwards [winding_eventually_eq Γ hwΓ, winding_eventually_eq Δ hwΔ,
      (isCompact_trace Γ).isClosed.isOpen_compl.mem_nhds hwΓ,
      (isCompact_trace Δ).isClosed.isOpen_compl.mem_nhds hwΔ] with a haΓ haΔ haoffΓ haoffΔ
    unfold pairDixon
    split_ifs with ha
    · exact hmatch a ha haoffΓ haoffΔ (haΓ.trans ((hnull w hw).trans haΔ.symm))
    · rfl

/-- Once the independently established pieces are matched, the continuation
vanishes by the Banach-valued Liouville theorem. -/
theorem pairDixon_eq_zero_of_pieces (Γ Δ : IntegralCycle) {f : ℂ → E} {U : Set ℂ}
    (hU : IsOpen U) (hf : DifferentiableOn ℂ f U)
    (hΓ : Γ.trace ⊆ U) (hΔ : Δ.trace ⊆ U)
    (hnull : ∀ w ∉ U, winding Γ w = winding Δ w)
    (hmatch : ∀ w ∈ U, w ∉ Γ.trace → w ∉ Δ.trace →
      winding Γ w = winding Δ w →
      Γ.lineIntegral (dslope f w) - Δ.lineIntegral (dslope f w) =
        dixonH2 Γ f w - dixonH2 Δ f w)
    (hwindΓ : ∀ᶠ w in cocompact ℂ, w ∉ Γ.trace ∧ winding Γ w = 0)
    (hwindΔ : ∀ᶠ w in cocompact ℂ, w ∉ Δ.trace ∧ winding Δ w = 0)
    (hdecayΓ : Tendsto (dixonH2 Γ f) (cocompact ℂ) (𝓝 0))
    (hdecayΔ : Tendsto (dixonH2 Δ f) (cocompact ℂ) (𝓝 0)) :
    ∀ w, pairDixon Γ Δ f U w = 0 := by
  have hd := differentiable_pairDixon Γ Δ hU hf hΓ hΔ hnull hmatch
  have heq : pairDixon Γ Δ f U =ᶠ[cocompact ℂ]
      fun w ↦ dixonH2 Γ f w - dixonH2 Δ f w := by
    filter_upwards [hwindΓ,hwindΔ] with w hwΓ hwΔ
    unfold pairDixon
    split_ifs with hw
    · exact hmatch w hw hwΓ.1 hwΔ.1 (hwΓ.2.trans hwΔ.2.symm)
    · rfl
  have hlim : Tendsto (pairDixon Γ Δ f U) (cocompact ℂ) (𝓝 0) := by
    have hsub := hdecayΓ.sub hdecayΔ
    simp only [sub_self] at hsub
    exact hsub.congr' heq.symm
  exact fun w ↦ hd.apply_eq_of_tendsto_cocompact w hlim

theorem lineIntegral_congr_on_trace (Γ : IntegralCycle) {f g : ℂ → E}
    (hfg : EqOn f g Γ.trace) : Γ.lineIntegral f = Γ.lineIntegral g := by
  unfold IntegralCycle.lineIntegral
  apply Finset.sum_congr rfl
  intro i hi
  apply intervalIntegral.integral_congr
  intro t ht
  rw [hfg (Γ.curve i t) ⟨i,t,ht,rfl⟩]

/-- Multiplication by the vanishing linear factor removes the divided
difference singularity, including on the diagonal itself. -/
theorem dslope_twist_eq (f : ℂ → E) {U : Set ℂ} (hU : IsOpen U)
    (hf : DifferentiableOn ℂ f U) {w : ℂ} (hw : w ∈ U) (z : ℂ) :
    dslope (fun a ↦ (a-w) • f a) w z = f z := by
  by_cases hzw : z = w
  · subst z
    rw [dslope_same]
    have hd := ((hasDerivAt_id w).sub_const w).smul
      ((hf w hw).differentiableAt (hU.mem_nhds hw)).hasDerivAt
    simpa using hd.deriv
  · rw [dslope_of_ne _ hzw]
    simp [slope, smul_smul, inv_mul_cancel₀ (sub_ne_zero.mpr hzw)]

theorem lineIntegral_eq_of_twisted_pairDixon_zero (Γ Δ : IntegralCycle)
    {f : ℂ → E} {U : Set ℂ} (hU : IsOpen U) (hf : DifferentiableOn ℂ f U)
    {w : ℂ} (hw : w ∈ U)
    (hzero : pairDixon Γ Δ (fun z ↦ (z-w) • f z) U w = 0) :
    Γ.lineIntegral f = Δ.lineIntegral f := by
  have hΓ : Γ.lineIntegral (dslope (fun z ↦ (z-w) • f z) w) = Γ.lineIntegral f :=
    lineIntegral_congr_on_trace Γ (fun z _ ↦ dslope_twist_eq f hU hf hw z)
  have hΔ : Δ.lineIntegral (dslope (fun z ↦ (z-w) • f z) w) = Δ.lineIntegral f :=
    lineIntegral_congr_on_trace Δ (fun z _ ↦ dslope_twist_eq f hU hf hw z)
  simp only [pairDixon, if_pos hw, hΓ, hΔ, sub_eq_zero] at hzero
  exact hzero

end Komorebi.PaperII.ReleaseCycleCauchy
