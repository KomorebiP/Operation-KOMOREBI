import Komorebi.SufficientResolution.MetricObstruction
import Komorebi.SufficientResolution.HilbertConditioning
import Komorebi.SufficientResolution.ReconstructionGlobalization

/-!
# Intrinsic obstruction norms in noisy globalization

Project local data to the compatible space and then take their actual quotient
class. The resulting bounded linear map has norm at most one. The intrinsic
class norm replaces the harmonic norm in the earlier error identities.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.IntrinsicGlobalization

open OrthogonalResolution HilbertGlobalization MetricObstruction HilbertConditioning

variable {G V W : Type*}
variable [AddCommGroup G] [Module ℝ G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V]
variable [NormedAddCommGroup W] [NormedSpace ℝ W]
variable (A : G →ₗ[ℝ] V) (delta : V →L[ℝ] W)
variable [(LinearMap.range A).HasOrthogonalProjection]
variable [(LinearMap.ker delta.toLinearMap).HasOrthogonalProjection]

/-- A compatible quotient class can be assigned to noisy local data by projection. -/
def projectedClass : V →L[ℝ] Globalization.ObstructionSpace A delta.toLinearMap :=
  ((Globalization.realizationsInKernel A delta.toLinearMap).mkQ.comp
    delta.ker.orthogonalProjectionOnto.toLinearMap).mkContinuous 1 (by
      intro v
      change ‖(Submodule.Quotient.mk (delta.ker.orthogonalProjectionOnto v) :
        Globalization.ObstructionSpace A delta.toLinearMap)‖ ≤ 1 * ‖v‖
      rw [one_mul]
      exact (Submodule.Quotient.norm_mk_le _ _).trans
        (delta.ker.norm_starProjection_apply_le v))

omit [(LinearMap.range A).HasOrthogonalProjection] in
theorem projectedClass_apply (v : V) :
    projectedClass A delta v = Globalization.obstructionClass A delta.toLinearMap
      (delta.ker.orthogonalProjectionOnto v) := rfl

/-- Projection discards inconsistency but does not alter the obstruction component. -/
theorem obstruction_projection (h : delta.toLinearMap.comp A = 0) (v : V) :
    obstruction (LinearMap.range A) delta.ker (delta.ker.starProjection v) =
      obstruction (LinearMap.range A) delta.ker v := by
  change delta.ker.starProjection (delta.ker.starProjection v) -
    (LinearMap.range A).starProjection (delta.ker.starProjection v) = _
  rw [Submodule.starProjection_eq_self_iff.mpr (delta.ker.starProjection_apply_mem v)]
  have he := congrArg (fun f : V →L[ℝ] V => f v)
    (Submodule.starProjection_comp_starProjection_of_le (range_le_kernel A delta h))
  change (LinearMap.range A).starProjection (delta.ker.starProjection v) =
    (LinearMap.range A).starProjection v at he
  rw [he]
  rfl

theorem projectedClass_norm (h : delta.toLinearMap.comp A = 0) (v : V) :
    ‖projectedClass A delta v‖ = ‖obstruction (LinearMap.range A) delta.ker v‖ := by
  rw [projectedClass_apply, norm_class_eq_obstruction A delta h]
  exact congrArg norm (obstruction_projection A delta h v)

omit [(LinearMap.range A).HasOrthogonalProjection] in
theorem projectedClass_norm_le (v : V) : ‖projectedClass A delta v‖ ≤ ‖v‖ :=
  (Submodule.Quotient.norm_mk_le _ _).trans (delta.ker.norm_starProjection_apply_le v)

omit [(LinearMap.range A).HasOrthogonalProjection] in
theorem projectedClass_opNorm_le : ‖projectedClass A delta‖ ≤ 1 :=
  ContinuousLinearMap.opNorm_le_bound _ (by norm_num) (by
    intro v
    simpa only [one_mul] using projectedClass_norm_le A delta v)

omit [(LinearMap.range A).HasOrthogonalProjection] in
theorem projectedClass_noise_bound (v w : V) :
    ‖projectedClass A delta v - projectedClass A delta w‖ ≤ ‖v-w‖ := by
  rw [← map_sub]
  exact projectedClass_norm_le A delta (v-w)

/-- Existing distance to realizability = intrinsic obstruction + inconsistency. -/
theorem intrinsic_distance_sq (h : delta.toLinearMap.comp A = 0) (v : V) :
    Metric.infDist v (LinearMap.range A : Set V)^2 =
      ‖projectedClass A delta v‖^2 + ‖inconsistency delta.ker v‖^2 := by
  rw [projectedClass_norm A delta h]
  exact infDist_sq_decomposition _ _ (range_le_kernel A delta h) v

theorem intrinsic_conditioned_distance (h : delta.toLinearMap.comp A = 0)
    (sigma : ℝ) (hs : 0 < sigma) (hc : CoerciveOffKernel delta sigma) (v : V) :
    Metric.infDist v (LinearMap.range A : Set V)^2 ≤
      ‖projectedClass A delta v‖^2 + (‖delta v‖/sigma)^2 := by
  rw [projectedClass_norm A delta h]
  exact conditioned_distance_sq delta _ (range_le_kernel A delta h) sigma hs hc v

theorem intrinsic_lower_bound (h : delta.toLinearMap.comp A = 0) (v : V) :
    ‖projectedClass A delta v‖ ≤ Metric.infDist v (LinearMap.range A : Set V) := by
  rw [projectedClass_norm A delta h]
  exact obstruction_lower_bound delta _ (range_le_kernel A delta h) v

theorem projectedClass_zero_iff (h : delta.toLinearMap.comp A = 0) (v : V) :
    projectedClass A delta v = 0 ↔ obstruction (LinearMap.range A) delta.ker v = 0 := by
  rw [← quotient_norm_zero_iff A delta h, projectedClass_norm A delta h, norm_eq_zero]

theorem realizable_iff_class_and_residual_zero (h : delta.toLinearMap.comp A = 0) (v : V) :
    (∃ g : G, A g = v) ↔ projectedClass A delta v = 0 ∧ delta v = 0 := by
  rw [projectedClass_zero_iff A delta h]
  have he := realizable_iff_components_zero (LinearMap.range A) delta.ker
    (range_le_kernel A delta h) v
  rw [inconsistency_zero_iff] at he
  exact he

omit [(LinearMap.range A).HasOrthogonalProjection] in
theorem projectedClass_on_compatible (v : LinearMap.ker delta.toLinearMap) :
    projectedClass A delta (v : V) = Globalization.obstructionClass A delta.toLinearMap v := by
  rw [projectedClass_apply]
  congr 1
  apply Subtype.ext
  exact Submodule.starProjection_eq_self_iff.mpr v.2

end Komorebi.SufficientResolution.IntrinsicGlobalization

namespace Komorebi.SufficientResolution.IntrinsicGlobalization

open OrthogonalResolution MinimumNormReconstruction ReconstructionGlobalization

variable {G V W : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable [NormedAddCommGroup W] [NormedSpace ℝ W]
variable (A : G →L[ℝ] V) [CompleteSpace A.range] (delta : V →L[ℝ] W)

/-- Intrinsic quotient norm in the error of the actually constructed source recovery. -/
theorem intrinsic_canonical_residual (h : delta.comp A = 0) (v : V) :
    ‖v-A (recover A v)‖^2 = ‖projectedClass A.toLinearMap delta v‖^2 +
      ‖inconsistency delta.ker v‖^2 := by
  rw [projectedClass_norm A.toLinearMap delta (congrArg ContinuousLinearMap.toLinearMap h)]
  exact canonical_residual_sq A delta h v

/-- A candidate source has intrinsic obstruction, inconsistency, and avoidable image error. -/
theorem intrinsic_candidate_total_error (h : delta.comp A = 0) (v : V) (g : G) :
    ‖v-A g‖^2 = ‖projectedClass A.toLinearMap delta v‖^2 +
      ‖inconsistency delta.ker v‖^2 + ‖A (g-recover A v)‖^2 := by
  rw [projectedClass_norm A.toLinearMap delta (congrArg ContinuousLinearMap.toLinearMap h)]
  exact candidate_total_error_sq A delta h v g

end Komorebi.SufficientResolution.IntrinsicGlobalization
