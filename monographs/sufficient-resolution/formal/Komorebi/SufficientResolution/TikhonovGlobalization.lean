import Komorebi.SufficientResolution.TikhonovBias
import Komorebi.SufficientResolution.IntrinsicGlobalization

/-!
# Regularization within the existing intrinsic globalization geometry

Positive regularization does not remove local obstruction or inconsistency.
The closed-range hypothesis below is only used to compare with the earlier
canonical pseudoinverse and quotient geometry, not to construct Tikhonov recovery.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.TikhonovGlobalization

open TikhonovConstruction TikhonovOptimality TikhonovBounds TikhonovBias
open MinimumNormReconstruction HilbertConditioning OrthogonalResolution HilbertGlobalization
open IntrinsicGlobalization

variable {G V W : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable [NormedAddCommGroup W] [NormedSpace ℝ W]
variable (A : G →L[ℝ] V) [CompleteSpace A.range] (lam : ℝ)

 theorem regularized_as_filtered_recover (hlam : 0 < lam) (v : V) :
    regularized A lam hlam v = regularized A lam hlam (A (recover A v)) := by
  have ho : v-A (recover A v) ∈ A.rangeᗮ := by
    rw [image_recover]
    exact Submodule.sub_starProjection_mem_orthogonal v
  have hz := regularized_ignores_range_orthogonal A lam hlam (v-A (recover A v)) ho
  rw [map_sub] at hz
  exact sub_eq_zero.mp hz

 theorem regularized_pseudoinverse_bias (hlam : 0 < lam) (v : V) :
    regularized A lam hlam v-recover A v = -(lam • resolvent A lam hlam (recover A v)) := by
  rw [regularized_as_filtered_recover]
  exact bias_identity A lam hlam (recover A v)

 theorem regularized_pseudoinverse_bound (hlam : 0 < lam)
    (alpha : ℝ) (ha : 0 < alpha) (hc : CoerciveOffKernel A alpha) (v : V) :
    ‖regularized A lam hlam v-recover A v‖ ≤ lam/(alpha^2+lam)*‖recover A v‖ := by
  rw [regularized_as_filtered_recover]
  exact identifiable_bias_bound A lam hlam alpha ha hc (recover A v) (recover_mem A v)

 theorem regularized_source_norm_le_pseudoinverse (hlam : 0 < lam) (v : V) :
    ‖regularized A lam hlam v‖ ≤ ‖recover A v‖ := by
  rw [regularized_as_filtered_recover]
  exact source_filter_bound A lam hlam (recover A v)

 theorem regularized_equals_pseudoinverse_iff (hlam : 0 < lam) (v : V) :
    regularized A lam hlam v = recover A v ↔ recover A v = 0 := by
  constructor
  · intro h
    have hb := regularized_pseudoinverse_bias A lam hlam v
    rw [h, sub_self] at hb
    have hz : resolvent A lam hlam (recover A v) = 0 :=
      (smul_eq_zero.mp (neg_eq_zero.mp hb.symm)).resolve_left hlam.ne'
    have he := normal_resolvent A lam hlam (recover A v)
    rw [hz, map_zero] at he
    exact he.symm
  · intro h
    rw [regularized_as_filtered_recover, h, map_zero, map_zero]

 theorem regularized_best_image_iff (hlam : 0 < lam) (v : V) :
    A (regularized A lam hlam v) = A.range.starProjection v ↔ recover A v = 0 := by
  constructor
  · intro h
    apply (regularized_equals_pseudoinverse_iff A lam hlam v).mp
    exact injective_on_kernel_orthogonal A (source_kernel_orthogonal A lam hlam v)
      (recover_mem A v) (h.trans (image_recover A v).symm)
  · intro h
    rw [(regularized_equals_pseudoinverse_iff A lam hlam v).mpr h, image_recover]

variable (delta : V →L[ℝ] W)

 theorem regularized_obstruction_zero (hlam : 0 < lam) (h : delta.comp A = 0) (v : V) :
    regularized A lam hlam (obstruction A.range delta.ker v) = 0 := by
  apply regularized_ignores_range_orthogonal
  exact (obstruction_mem A.range delta.ker
    (range_le_kernel A.toLinearMap delta (congrArg ContinuousLinearMap.toLinearMap h)) v).2

omit [CompleteSpace A.range] in
 theorem regularized_inconsistency_zero (hlam : 0 < lam) (h : delta.comp A = 0) (v : V) :
    regularized A lam hlam (inconsistency delta.ker v) = 0 := by
  apply regularized_ignores_range_orthogonal
  exact Submodule.orthogonal_le
    (range_le_kernel A.toLinearMap delta (congrArg ContinuousLinearMap.toLinearMap h))
    (inconsistency_mem delta.ker v)

 theorem objective_intrinsic_decomposition (h : delta.comp A = 0) (v : V) (g : G) :
    objective A lam v g = ‖projectedClass A.toLinearMap delta v‖^2+
      ‖inconsistency delta.ker v‖^2+‖A (g-recover A v)‖^2+lam*‖g‖^2 := by
  unfold objective
  rw [norm_sub_rev, intrinsic_candidate_total_error A delta h v g]

 theorem regularized_intrinsic_error (hlam : 0 < lam) (h : delta.comp A = 0) (v : V) :
    ‖v-A (regularized A lam hlam v)‖^2 = ‖projectedClass A.toLinearMap delta v‖^2+
      ‖inconsistency delta.ker v‖^2+
        ‖A (regularized A lam hlam v-recover A v)‖^2 :=
  intrinsic_candidate_total_error A delta h v (regularized A lam hlam v)

end Komorebi.SufficientResolution.TikhonovGlobalization
