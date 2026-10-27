import KomorebiVerification.PaperII.ReleaseCycleParameter
import KomorebiVerification.PaperII.ReleaseCycleDecay
import ReleaseCyclePrimitive
import Mathlib.Analysis.Complex.HasPrimitives

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option maxHeartbeats 1000000
noncomputable section
namespace Komorebi.PaperII.ReleaseCycleWinding
open Set MeasureTheory Filter
open scoped Topology
open Komorebi.PaperII.ReleaseAnalyticContour
open Komorebi.PaperII.ReleaseCycleParameter

/-- Winding defined by the actual finite cycle integral, off the trace. -/
def winding (Γ : IntegralCycle) (w : ℂ) : ℂ :=
  (2 * (Real.pi : ℂ) * Complex.I)⁻¹ *
    Γ.lineIntegral (fun z => (z - w)⁻¹)

theorem hasDerivAt_inverse_kernel (z w : ℂ) (hzw : z - w ≠ 0) :
    HasDerivAt (fun a : ℂ => (z - a)⁻¹) (((z - w)^2)⁻¹) w := by
  convert! ((hasDerivAt_const w z).sub (hasDerivAt_id w)).inv hzw using 1
  simp

theorem hasDerivAt_kernelIntegral (Γ : IntegralCycle) {w : ℂ} (hw : w ∉ Γ.trace) :
    HasDerivAt (fun a => Γ.lineIntegral (fun z => (z - a)⁻¹))
      (Γ.lineIntegral (fun z => ((z - w)^2)⁻¹)) w := by
  obtain ⟨ε, hε, haway⟩ := exists_ball_away_trace Γ hw
  have hne : ∀ a ∈ Metric.ball w ε, ∀ z ∈ Γ.trace, z - a ≠ 0 := by
    intro a ha z hz hzero
    have := haway z hz a ha
    rw [hzero, norm_zero] at this
    linarith
  refine hasDerivAt_lineIntegral Γ
    (f := fun a z => (z-a)⁻¹) (f' := fun a z => ((z-a)^2)⁻¹)
    (s := Metric.ball w ε) (Metric.ball_mem_nhds w hε)
    ?_ ?_ ?_ ((ε^2)⁻¹) ?_
  · intro a ha
    exact (continuousOn_id.sub continuousOn_const).inv₀ fun z hz => hne a ha z hz
  · exact ((continuousOn_id.sub continuousOn_const).pow 2).inv₀
      fun z hz => pow_ne_zero 2 (hne w (Metric.mem_ball_self hε) z hz)
  · intro a ha z hz
    exact hasDerivAt_inverse_kernel z a (hne a ha z hz)
  · intro a ha z hz
    simp only [norm_inv, norm_pow]
    apply inv_anti₀ (by positivity)
    nlinarith [haway z hz a ha, norm_nonneg (z-a)]

theorem hasDerivAt_winding (Γ : IntegralCycle) {w : ℂ} (hw : w ∉ Γ.trace) :
    HasDerivAt (winding Γ)
      ((2 * (Real.pi : ℂ) * Complex.I)⁻¹ *
        Γ.lineIntegral (fun z => ((z - w)^2)⁻¹)) w := by
  exact (hasDerivAt_kernelIntegral Γ hw).const_mul _

theorem hasDerivAt_inverse_primitive (z w : ℂ) (hzw : z - w ≠ 0) :
    HasDerivAt (fun a : ℂ => -(a-w)⁻¹) (((z-w)^2)⁻¹) z := by
  convert! (((hasDerivAt_id z).sub_const w).inv hzw).neg using 1
  simp only [id_eq]
  ring

theorem integral_inverseSquare_eq_zero (Γ : IntegralCycle) {w : ℂ}
    (hw : w ∉ Γ.trace) : Γ.lineIntegral (fun z => ((z-w)^2)⁻¹) = 0 := by
  have htrace : Γ.trace ⊆ {w}ᶜ := by
    intro z hz
    simpa only [mem_compl_iff, mem_singleton_iff] using ne_of_mem_of_not_mem hz hw
  have hF : DifferentiableOn ℂ (fun z : ℂ => -(z-w)⁻¹) {w}ᶜ := by
    intro z hz
    exact (hasDerivAt_inverse_primitive z w (sub_ne_zero.mpr hz)).differentiableAt.differentiableWithinAt
  have hzero := Γ.lineIntegral_deriv_eq_zero isOpen_compl_singleton htrace hF
  rw [← hzero]
  unfold IntegralCycle.lineIntegral
  apply Finset.sum_congr rfl
  intro i hi
  apply intervalIntegral.integral_congr
  intro t ht
  change Γ.velocity i t • ((Γ.curve i t-w)^2)⁻¹ =
    Γ.velocity i t • deriv (fun z : ℂ => -(z-w)⁻¹) (Γ.curve i t)
  have hz : Γ.curve i t ∈ Γ.trace := ⟨i,t,ht,rfl⟩
  exact congrArg (fun q : ℂ => Γ.velocity i t • q)
    (hasDerivAt_inverse_primitive _ w
      (sub_ne_zero.mpr (ne_of_mem_of_not_mem hz hw))).deriv.symm

theorem hasDerivAt_winding_zero (Γ : IntegralCycle) {w : ℂ} (hw : w ∉ Γ.trace) :
    HasDerivAt (winding Γ) 0 w := by
  simpa only [integral_inverseSquare_eq_zero Γ hw, mul_zero] using hasDerivAt_winding Γ hw

/-- Winding is locally constant off the trace for arbitrary integrable
velocities. The proof uses the scalar primitive FTC, not winding integrality. -/
theorem winding_eventually_eq (Γ : IntegralCycle) {w : ℂ} (hw : w ∉ Γ.trace) :
    ∀ᶠ a in 𝓝 w, winding Γ a = winding Γ w := by
  obtain ⟨ε, hε, haway⟩ := exists_ball_away_trace Γ hw
  have hoff : ∀ a ∈ Metric.ball w ε, a ∉ Γ.trace := by
    intro a ha hz
    have := haway a hz a ha
    simp only [sub_self, norm_zero] at this
    linarith
  filter_upwards [Metric.ball_mem_nhds w hε] with a ha
  exact Metric.isOpen_ball.is_const_of_deriv_eq_zero (convex_ball w ε).isPreconnected
    (fun z hz => (hasDerivAt_winding_zero Γ (hoff z hz)).differentiableAt.differentiableWithinAt)
    (fun z hz => (hasDerivAt_winding_zero Γ (hoff z hz)).deriv)
    ha (Metric.mem_ball_self hε)

theorem lineIntegral_eq_zero_of_holomorphic_ball (Γ : IntegralCycle) {f : ℂ → ℂ}
    {c : ℂ} {R : ℝ} (htrace : Γ.trace ⊆ Metric.ball c R)
    (hf : DifferentiableOn ℂ f (Metric.ball c R)) : Γ.lineIntegral f = 0 := by
  obtain ⟨F,hF⟩ := hf.isExactOn_ball
  have hFdif : DifferentiableOn ℂ F (Metric.ball c R) :=
    fun z hz => (hF z hz).differentiableAt.differentiableWithinAt
  have hzero := Γ.lineIntegral_deriv_eq_zero Metric.isOpen_ball htrace hFdif
  rw [← hzero]
  unfold IntegralCycle.lineIntegral
  apply Finset.sum_congr rfl
  intro i hi
  apply intervalIntegral.integral_congr
  intro t ht
  exact congrArg (fun q : ℂ => Γ.velocity i t • q)
    (hF _ (htrace ⟨i,t,ht,rfl⟩)).deriv.symm

/-- The actual winding integral vanishes sufficiently far from the compact trace. -/
theorem winding_eq_zero_of_far (Γ : IntegralCycle) {R : ℝ}
    (htrace : Γ.trace ⊆ Metric.ball 0 R) {w : ℂ} (hw : R ≤ ‖w‖) : winding Γ w = 0 := by
  have hzero : Γ.lineIntegral (fun z => (z-w)⁻¹) = 0 := by
    apply lineIntegral_eq_zero_of_holomorphic_ball Γ htrace
    intro z hz
    have hzw : z-w ≠ 0 := by
      apply sub_ne_zero.mpr
      intro heq
      subst w
      simp only [Metric.mem_ball, dist_zero_right] at hz
      linarith
    exact (((hasDerivAt_id z).sub_const w).inv hzw).differentiableAt.differentiableWithinAt
  simp only [winding,hzero,mul_zero]

theorem winding_eventually_zero (Γ : IntegralCycle) :
    ∀ᶠ w in cocompact ℂ, winding Γ w = 0 := by
  obtain ⟨R,hR⟩ := (isCompact_trace Γ).bddAbove_image continuousOn_id.norm
  have htrace : Γ.trace ⊆ Metric.ball 0 (R+1) := by
    intro z hz
    simp only [Metric.mem_ball,dist_zero_right]
    exact lt_of_le_of_lt (hR (mem_image_of_mem _ hz)) (lt_add_one R)
  filter_upwards [Komorebi.PaperII.ReleaseCycleDecay.norm_gt_mem_cocompact (R+1)] with w hw
  exact winding_eq_zero_of_far Γ htrace hw.le

end Komorebi.PaperII.ReleaseCycleWinding
