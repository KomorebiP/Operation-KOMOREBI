import Komorebi.SufficientResolution.ClosedRangeReconstruction
import Komorebi.SufficientResolution.HilbertGlobalization

/-!
# Source recovery integrated with local compatibility and obstruction

alpha controls the source inverse A. sigma controls the compatibility map delta.
The formulas retain both and never infer source identifiability from compatibility.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.ReconstructionGlobalization

open MinimumNormReconstruction MinimumNormOptimality SourceConditioning
open OrthogonalResolution HilbertGlobalization HilbertConditioning

variable {G V W : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable [NormedAddCommGroup W] [NormedSpace ℝ W]
variable (A : G →L[ℝ] V) [CompleteSpace A.range] (delta : V →L[ℝ] W)

 theorem recover_obstruction_zero (h : delta.comp A = 0) (v : V) :
    recover A (obstruction A.range delta.ker v) = 0 := by
  apply (recover_eq_zero_iff A _).mpr
  have hr : A.range ≤ delta.ker := range_le_kernel A.toLinearMap delta
    (congrArg ContinuousLinearMap.toLinearMap h)
  exact (obstruction_mem A.range delta.ker hr v).2

 theorem recover_inconsistency_zero (h : delta.comp A = 0) (v : V) :
    recover A (inconsistency delta.ker v) = 0 := by
  apply (recover_eq_zero_iff A _).mpr
  have hr : A.range ≤ delta.ker := range_le_kernel A.toLinearMap delta
    (congrArg ContinuousLinearMap.toLinearMap h)
  exact Submodule.orthogonal_le hr (inconsistency_mem delta.ker v)

 theorem recover_compatible_projection (h : delta.comp A = 0) (v : V) :
    recover A (delta.ker.starProjection v) = recover A v := by
  have he : delta.ker.starProjection v = A.range.starProjection v + obstruction A.range delta.ker v := by
    change delta.ker.starProjection v = A.range.starProjection v +
      (delta.ker.starProjection v - A.range.starProjection v)
    abel
  rw [he, map_add, recover_obstruction_zero A delta h v, add_zero, recover_projected_data]

 theorem canonical_residual_sq (h : delta.comp A = 0) (v : V) :
    ‖v-A (recover A v)‖^2 =
      ‖obstruction A.range delta.ker v‖^2 + ‖inconsistency delta.ker v‖^2 := by
  rw [image_recover]
  exact error_norm_sq _ _ (range_le_kernel A.toLinearMap delta
    (congrArg ContinuousLinearMap.toLinearMap h)) v

/-- Total fitting error = irreducible local error + the candidate's avoidable image error. -/
 theorem candidate_total_error_sq (h : delta.comp A = 0) (v : V) (g : G) :
    ‖v-A g‖^2 = ‖obstruction A.range delta.ker v‖^2 +
      ‖inconsistency delta.ker v‖^2 + ‖A (g-recover A v)‖^2 := by
  rw [candidate_error_decomposition, canonical_residual_sq A delta h]

 theorem canonical_conditioned_residual (h : delta.comp A = 0)
    (sigma : ℝ) (hs : 0 < sigma) (hd : CoerciveOffKernel delta sigma) (v : V) :
    ‖v-A (recover A v)‖^2 ≤
      ‖obstruction A.range delta.ker v‖^2 + (‖delta v‖/sigma)^2 := by
  rw [recover_best_error]
  exact conditioned_distance_sq delta A.range (range_le_kernel A.toLinearMap delta
    (congrArg ContinuousLinearMap.toLinearMap h)) sigma hs hd v

/-- Both source and compatibility conditioning occur in one explicit certificate. -/
 theorem two_condition_reconstruction (h : delta.comp A = 0)
    (alpha sigma : ℝ) (ha : 0 < alpha) (hs : 0 < sigma)
    (hA : CoerciveOffKernel A alpha) (hd : CoerciveOffKernel delta sigma) (v : V) :
    ‖recover A v‖ ≤ ‖v‖/alpha ∧
      ‖v-A (recover A v)‖^2 ≤
        ‖obstruction A.range delta.ker v‖^2 + (‖delta v‖/sigma)^2 :=
  ⟨recover_bound A alpha ha hA v, canonical_conditioned_residual A delta h sigma hs hd v⟩

 theorem exact_realization_iff_components (h : delta.comp A = 0) (v : V) :
    A (recover A v) = v ↔
      obstruction A.range delta.ker v = 0 ∧ inconsistency delta.ker v = 0 := by
  rw [image_recover, Submodule.starProjection_eq_self_iff]
  exact realizable_iff_components_zero _ _ (range_le_kernel A.toLinearMap delta
    (congrArg ContinuousLinearMap.toLinearMap h)) v

end Komorebi.SufficientResolution.ReconstructionGlobalization
