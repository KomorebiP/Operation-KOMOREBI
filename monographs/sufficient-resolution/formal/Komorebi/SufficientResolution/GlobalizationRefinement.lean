import Komorebi.SufficientResolution.HilbertConditioning

/-!
# Exact gains from enlarging the realizable space

R0 <= R1 <= K models additional global realizations without changing local
compatibility. The recovered orthogonal component accounts exactly for the
decrease in obstruction and best-reconstruction error.
-/

set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.GlobalizationRefinement

open OrthogonalResolution

variable {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]
variable (R₀ R₁ K : Submodule ℝ V)
variable [R₀.HasOrthogonalProjection] [R₁.HasOrthogonalProjection] [K.HasOrthogonalProjection]

 theorem obstruction_refinement_identity (v : V) :
    obstruction R₀ K v = obstruction R₁ K v + obstruction R₀ R₁ v := by
  simp only [obstruction, sub_apply]
  abel

 theorem gain_orthogonal_remaining (h₀₁ : R₀ ≤ R₁) (h₁K : R₁ ≤ K) (v : V) :
    inner ℝ (obstruction R₀ R₁ v) (obstruction R₁ K v) = 0 :=
  (obstruction_mem R₁ K h₁K v).2 _ (obstruction_mem R₀ R₁ h₀₁ v).1

 theorem obstruction_refinement_sq (h₀₁ : R₀ ≤ R₁) (h₁K : R₁ ≤ K) (v : V) :
    ‖obstruction R₀ K v‖ ^ 2 =
      ‖obstruction R₁ K v‖ ^ 2 + ‖obstruction R₀ R₁ v‖ ^ 2 := by
  rw [obstruction_refinement_identity R₀ R₁ K v]
  simpa only [pow_two] using norm_add_sq_eq_norm_sq_add_norm_sq_of_inner_eq_zero _ _
    (inner_eq_zero_symm.mpr (gain_orthogonal_remaining R₀ R₁ K h₀₁ h₁K v))

 theorem distance_refinement_sq (h₀₁ : R₀ ≤ R₁) (v : V) :
    Metric.infDist v (R₀ : Set V) ^ 2 =
      Metric.infDist v (R₁ : Set V) ^ 2 + ‖obstruction R₀ R₁ v‖ ^ 2 := by
  have hp := infDist_sq_decomposition R₀ R₁ h₀₁ v
  rw [infDist_eq_error R₁ v]
  change Metric.infDist v (R₀ : Set V) ^ 2 =
    ‖inconsistency R₁ v‖ ^ 2 + ‖obstruction R₀ R₁ v‖ ^ 2
  linarith

 theorem obstruction_decreases (h₀₁ : R₀ ≤ R₁) (h₁K : R₁ ≤ K) (v : V) :
    ‖obstruction R₁ K v‖ ≤ ‖obstruction R₀ K v‖ := by
  have hp := obstruction_refinement_sq R₀ R₁ K h₀₁ h₁K v
  nlinarith [sq_nonneg ‖obstruction R₀ R₁ v‖,
    norm_nonneg (obstruction R₀ K v), norm_nonneg (obstruction R₁ K v)]

 theorem no_gain_iff_equal_distance (h₀₁ : R₀ ≤ R₁) (v : V) :
    Metric.infDist v (R₀ : Set V) = Metric.infDist v (R₁ : Set V) ↔
      obstruction R₀ R₁ v = 0 := by
  have hp := distance_refinement_sq R₀ R₁ h₀₁ v
  constructor
  · intro he
    rw [he] at hp
    apply norm_eq_zero.mp
    nlinarith [norm_nonneg (obstruction R₀ R₁ v)]
  · intro hz
    rw [hz, norm_zero, zero_pow (by decide : 2 ≠ 0), add_zero] at hp
    nlinarith [Metric.infDist_nonneg (x := v) (s := (R₀ : Set V)),
      Metric.infDist_nonneg (x := v) (s := (R₁ : Set V))]

 theorem recovered_component_eq_projection_difference (v : V) :
    obstruction R₀ R₁ v = realized R₁ v - realized R₀ v := rfl

 theorem obstruction_invariant_realizable_shift (h : R₀ ≤ K) (v r : V) (hr : r ∈ R₀) :
    obstruction R₀ K (v+r) = obstruction R₀ K v := by
  rw [map_add]
  have hz : obstruction R₀ K r = 0 :=
    (obstruction_zero_iff_of_compatible R₀ K r (h hr)).mpr hr
  rw [hz, add_zero]

 theorem inconsistency_invariant_compatible_shift (v k : V) (hk : k ∈ K) :
    inconsistency K (v+k) = inconsistency K v := by
  rw [map_add, (inconsistency_zero_iff K k).mpr hk, add_zero]

end Komorebi.SufficientResolution.GlobalizationRefinement
