import Komorebi.SufficientResolution.TikhonovConvergence
import Komorebi.SufficientResolution.ClosedRangeReconstruction

/-!
# Strong versus operator-norm convergence

A recovery error below one in operator norm forces closed range. For a nonclosed
range the regularized source-filter error has norm exactly one at every positive
parameter, despite strong convergence on each fixed source.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.UniformRegularization

open TikhonovConstruction TikhonovBias TikhonovDensity TikhonovConvergence
open ClosedRangeReconstruction HilbertConditioning MinimumNormReconstruction
open Filter Topology

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

/-- Actual bounded operator measuring the identifiable-source error. -/
def sourceError (lam : ℝ) (hlam : 0 < lam) : G →L[ℝ] G :=
  (regularized A lam hlam).comp A - A.kerᗮ.starProjection

 theorem sourceError_apply (lam : ℝ) (hlam : 0 < lam) (g : G) :
    sourceError A lam hlam g = regularized A lam hlam (A g)-A.kerᗮ.starProjection g := rfl

 theorem sourceError_norm_le_one (lam : ℝ) (hlam : 0 < lam) :
    ‖sourceError A lam hlam‖ ≤ 1 := by
  apply ContinuousLinearMap.opNorm_le_bound _ zero_le_one
  intro g
  simpa only [one_mul, sourceError_apply] using projected_bias_bound A lam hlam g

omit [CompleteSpace V] in
 theorem closed_range_of_approximate_recovery (B : V →L[ℝ] G)
    (hc : ‖B.comp A-A.kerᗮ.starProjection‖ < 1) : IsClosed (A.range : Set V) := by
  let c := ‖B.comp A-A.kerᗮ.starProjection‖
  have hd : 0 < ‖B‖+1 := by positivity
  have ha : 0 < (1-c)/(‖B‖+1) := div_pos (sub_pos.mpr hc) hd
  apply closed_range_of_coercivity A ((1-c)/(‖B‖+1)) ha
  intro x hx
  have hp : A.kerᗮ.starProjection x = x := Submodule.starProjection_eq_self_iff.mpr hx
  have he : ‖B (A x)-x‖ ≤ c*‖x‖ := by
    simpa only [sub_apply, ContinuousLinearMap.comp_apply, hp]
      using (B.comp A-A.kerᗮ.starProjection).le_opNorm x
  have ht : ‖x‖ ≤ c*‖x‖+‖B‖*‖A x‖ := by
    calc
      ‖x‖ = ‖(x-B (A x))+B (A x)‖ := by rw [sub_add_cancel]
      _ ≤ ‖x-B (A x)‖+‖B (A x)‖ := norm_add_le _ _
      _ ≤ c*‖x‖+‖B‖*‖A x‖ := by
        rw [norm_sub_rev]
        exact add_le_add he (B.le_opNorm _)
  rw [div_mul_eq_mul_div]
  apply (div_le_iff₀ hd).mpr
  nlinarith [norm_nonneg (A x)]

 theorem nonclosed_sourceError_norm (hn : ¬ IsClosed (A.range : Set V))
    (lam : ℝ) (hlam : 0 < lam) : ‖sourceError A lam hlam‖ = 1 := by
  apply le_antisymm (sourceError_norm_le_one A lam hlam)
  apply le_of_not_gt
  intro h
  exact hn (closed_range_of_approximate_recovery A (regularized A lam hlam) h)

 theorem conditioned_sourceError_norm (alpha : ℝ) (ha : 0 < alpha)
    (hc : CoerciveOffKernel A alpha) (lam : ℝ) (hlam : 0 < lam) :
    ‖sourceError A lam hlam‖ ≤ lam/(alpha^2+lam) := by
  have hr : 0 ≤ lam/(alpha^2+lam) := by positivity
  apply ContinuousLinearMap.opNorm_le_bound _ hr
  intro g
  calc
    ‖sourceError A lam hlam g‖ =
        ‖regularized A lam hlam (A (A.kerᗮ.starProjection g))-A.kerᗮ.starProjection g‖ := by
      rw [source_projection_image]; rfl
    _ ≤ lam/(alpha^2+lam)*‖A.kerᗮ.starProjection g‖ :=
      identifiable_bias_bound A lam hlam alpha ha hc _ (A.kerᗮ.starProjection_apply_mem g)
    _ ≤ lam/(alpha^2+lam)*‖g‖ := mul_le_mul_of_nonneg_left
      (A.kerᗮ.norm_starProjection_apply_le g) hr

 theorem closed_sourceError_tendsto_zero (hc : IsClosed (A.range : Set V))
    {ι : Type*} (f : Filter ι) (lam : ι → ℝ) (hlam : ∀ i, 0 < lam i)
    (hlim : Tendsto lam f (𝓝 0)) :
    Tendsto (fun i => sourceError A (lam i) (hlam i)) f (𝓝 0) := by
  obtain ⟨alpha, ha, hco⟩ := closed_range_has_coercivity A hc
  have hb : Tendsto (fun i => lam i/(alpha^2+lam i)) f (𝓝 0) := by
    have h := hlim.div (tendsto_const_nhds.add hlim) (by positivity : alpha^2+0 ≠ 0)
    have he : (lam / (fun i => alpha^2+lam i)) =
        (fun i => lam i/(alpha^2+lam i)) := by
      funext i
      exact Pi.div_apply _ _ i
    rw [he] at h
    simpa only [add_zero, zero_div] using h
  exact squeeze_zero_norm (fun i => conditioned_sourceError_norm A alpha ha hco (lam i) (hlam i)) hb

 theorem uniform_convergence_iff_closed_range {ι : Type*} (f : Filter ι) [NeBot f]
    (lam : ι → ℝ) (hlam : ∀ i, 0 < lam i) (hlim : Tendsto lam f (𝓝 0)) :
    Tendsto (fun i => sourceError A (lam i) (hlam i)) f (𝓝 0) ↔
      IsClosed (A.range : Set V) := by
  constructor
  · intro ht
    by_contra hn
    have hnorm := ht.norm
    have hconst : Tendsto (fun _ : ι => (1 : ℝ)) f (𝓝 0) := by
      simpa only [nonclosed_sourceError_norm A hn, norm_zero] using hnorm
    have : (1 : ℝ) = 0 := tendsto_nhds_unique tendsto_const_nhds hconst
    exact one_ne_zero this
  · exact fun hc => closed_sourceError_tendsto_zero A hc f lam hlam hlim

end Komorebi.SufficientResolution.UniformRegularization
