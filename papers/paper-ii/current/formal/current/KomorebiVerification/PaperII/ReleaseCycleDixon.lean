import KomorebiVerification.PaperII.ReleaseCycleWinding
import Mathlib.Analysis.Calculus.DSlope
import Mathlib.Analysis.Complex.Liouville

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option maxHeartbeats 1000000
noncomputable section
namespace Komorebi.PaperII.ReleaseCycleDixon
open Set MeasureTheory Filter
open scoped Topology BigOperators
open Komorebi.PaperII.ReleaseAnalyticContour
open Komorebi.PaperII.ReleaseCycleParameter
open Komorebi.PaperII.ReleaseCycleWinding

variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
variable [NormedSpace ℝ E] [IsScalarTower ℝ ℂ E] [CompleteSpace E]

def dixonH2 (Γ : IntegralCycle) (f : ℂ → E) (w : ℂ) : E :=
  Γ.lineIntegral (fun z => (z-w)⁻¹ • f z)

omit [IsScalarTower ℝ ℂ E] [CompleteSpace E] in
/-- The off-trace half of Dixon's continuation is holomorphic for every
continuous Banach-valued density on the actual finite cycle. -/
theorem hasDerivAt_dixonH2 (Γ : IntegralCycle) {f : ℂ → E}
    (hf : ContinuousOn f Γ.trace) {w : ℂ} (hw : w ∉ Γ.trace) :
    HasDerivAt (dixonH2 Γ f)
      (Γ.lineIntegral (fun z => ((z-w)^2)⁻¹ • f z)) w := by
  obtain ⟨ε, hε, haway⟩ := exists_ball_away_trace Γ hw
  obtain ⟨M, hM⟩ := (isCompact_trace Γ).bddAbove_image hf.norm
  have hne : ∀ a ∈ Metric.ball w ε, ∀ z ∈ Γ.trace, z - a ≠ 0 := by
    intro a ha z hz hzero
    have := haway z hz a ha
    rw [hzero, norm_zero] at this
    linarith
  refine hasDerivAt_lineIntegral Γ
    (f := fun a z => (z-a)⁻¹ • f z) (f' := fun a z => ((z-a)^2)⁻¹ • f z)
    (s := Metric.ball w ε)
    (Metric.ball_mem_nhds w hε) ?_ ?_ ?_ ((ε^2)⁻¹ * max M 0) ?_
  · intro a ha
    exact ((continuousOn_id.sub continuousOn_const).inv₀
      fun z hz => hne a ha z hz).smul hf
  · exact (((continuousOn_id.sub continuousOn_const).pow 2).inv₀
      fun z hz => pow_ne_zero 2 (hne w (Metric.mem_ball_self hε) z hz)).smul hf
  · intro a ha z hz
    exact (hasDerivAt_inverse_kernel z a (hne a ha z hz)).smul_const (f z)
  · intro a ha z hz
    rw [norm_smul]
    apply mul_le_mul
    · simp only [norm_inv, norm_pow]
      apply inv_anti₀ (by positivity)
      nlinarith [haway z hz a ha, norm_nonneg (z-a)]
    · exact le_max_of_le_left (hM (mem_image_of_mem _ hz))
    · exact norm_nonneg _
    · positivity

omit [IsScalarTower ℝ ℂ E] [CompleteSpace E] in
/-- Decay bound at infinity in terms of the actual velocity length. -/
theorem norm_dixonH2_le (Γ : IntegralCycle) {f : ℂ → E} (R M : ℝ)
    (_hM : 0 ≤ M) (hR : ∀ z ∈ Γ.trace, ‖z‖ ≤ R)
    (hf : ∀ z ∈ Γ.trace, ‖f z‖ ≤ M) {w : ℂ} (hw : R < ‖w‖) :
    ‖dixonH2 Γ f w‖ ≤ Γ.length * ((‖w‖-R)⁻¹ * M) := by
  apply Γ.norm_lineIntegral_le
  intro z hz
  rw [norm_smul, norm_inv]
  apply mul_le_mul
  · apply inv_anti₀ (sub_pos.mpr hw)
    have htri := norm_sub_norm_le w z
    rw [norm_sub_rev] at htri
    linarith [hR z hz]
  · exact hf z hz
  · exact norm_nonneg _
  · positivity

omit [IsScalarTower ℝ ℂ E] [CompleteSpace E] in
theorem lineIntegral_congr (Γ : IntegralCycle) {f g : ℂ → E}
    (hfg : EqOn f g Γ.trace) : Γ.lineIntegral f = Γ.lineIntegral g := by
  unfold IntegralCycle.lineIntegral
  apply Finset.sum_congr rfl
  intro i hi
  apply intervalIntegral.integral_congr
  intro t ht
  exact congrArg (fun a : E => Γ.velocity i t • a) (hfg ⟨i,t,ht,rfl⟩)

/-- The algebraic identity underlying Dixon's continuation. It holds for an
arbitrary Banach density continuous on the trace, with no holomorphy hypothesis. -/
theorem lineIntegral_dslope_eq_dixonH2_sub (Γ : IntegralCycle) {f : ℂ → E}
    (hf : ContinuousOn f Γ.trace) {w : ℂ} (hw : w ∉ Γ.trace) :
    Γ.lineIntegral (dslope f w) = dixonH2 Γ f w -
      Γ.lineIntegral (fun z => (z-w)⁻¹) • f w := by
  have hk : ContinuousOn (fun z : ℂ => (z-w)⁻¹) Γ.trace :=
    (continuousOn_id.sub continuousOn_const).inv₀
      fun z hz => sub_ne_zero.mpr (ne_of_mem_of_not_mem hz hw)
  have heq : Γ.lineIntegral (dslope f w) =
      Γ.lineIntegral (fun z => (z-w)⁻¹ • f z - (z-w)⁻¹ • f w) := by
    apply lineIntegral_congr Γ
    intro z hz
    rw [dslope_of_ne f (ne_of_mem_of_not_mem hz hw), slope_def_module, smul_sub]
  rw [heq, Γ.lineIntegral_sub (f := fun z => (z-w)⁻¹ • f z)
    (g := fun z => (z-w)⁻¹ • f w) (hk.smul hf) (hk.smul continuousOn_const)]
  have hmap := Γ.lineIntegral_map (ContinuousLinearMap.toSpanSingleton ℂ (f w)) hk
  exact congrArg (fun q : E => dixonH2 Γ f w - q) hmap

theorem kernelIntegral_eq_of_winding_eq (Γ Δ : IntegralCycle) {w : ℂ}
    (hw : winding Γ w = winding Δ w) :
    Γ.lineIntegral (fun z => (z-w)⁻¹) = Δ.lineIntegral (fun z => (z-w)⁻¹) := by
  have hc : (2 * (Real.pi : ℂ) * Complex.I)⁻¹ ≠ 0 := by
    simp [Real.pi_ne_zero]
  exact (mul_left_cancel₀ hc) hw

theorem pairH1H2match (Γ Δ : IntegralCycle) {f : ℂ → E}
    (hfΓ : ContinuousOn f Γ.trace) (hfΔ : ContinuousOn f Δ.trace)
    {w : ℂ} (hwΓ : w ∉ Γ.trace) (hwΔ : w ∉ Δ.trace)
    (hwind : winding Γ w = winding Δ w) :
    Γ.lineIntegral (dslope f w) - Δ.lineIntegral (dslope f w) =
      dixonH2 Γ f w - dixonH2 Δ f w := by
  rw [lineIntegral_dslope_eq_dixonH2_sub Γ hfΓ hwΓ,
    lineIntegral_dslope_eq_dixonH2_sub Δ hfΔ hwΔ,
    kernelIntegral_eq_of_winding_eq Γ Δ hwind]
  abel

end Komorebi.PaperII.ReleaseCycleDixon
