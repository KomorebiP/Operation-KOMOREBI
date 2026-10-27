import Komorebi.SufficientResolution.TikhonovBias
import Mathlib.Analysis.InnerProductSpace.Projection.Submodule

/-!
# Density and approximation certificates for regularized source filters

The normal range is dense in the identifiable source space even when range(A)
is not closed. The approximation estimate is uniform in the positive parameter.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.TikhonovDensity

open TikhonovConstruction TikhonovBias MinimumNormReconstruction

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

/-- The unregularized normal operator, with its actual range. -/
def gram : G →L[ℝ] G := A.adjoint.comp A

 theorem gram_apply (x : G) : gram A x = A.adjoint (A x) := rfl

 theorem gram_kernel : (gram A).ker = A.ker := by
  ext x
  change A.adjoint (A x) = 0 ↔ A x = 0
  constructor
  · intro h
    have he := congrArg (fun y : G => inner ℝ y x) h
    rw [ContinuousLinearMap.adjoint_inner_left, inner_zero_left] at he
    exact (inner_self_eq_zero.mp he)
  · intro h
    rw [h, map_zero]

 theorem gram_range_orthogonal : (gram A).rangeᗮ = A.ker := by
  ext x
  constructor
  · intro hx
    have he := hx (gram A x) ((gram A).mem_range_self x)
    change inner ℝ (A.adjoint (A x)) x = 0 at he
    rw [ContinuousLinearMap.adjoint_inner_left] at he
    exact inner_self_eq_zero.mp he
  · intro hx
    change A x = 0 at hx
    rintro y ⟨w, rfl⟩
    change inner ℝ (A.adjoint (A w)) x = 0
    rw [ContinuousLinearMap.adjoint_inner_left, hx, inner_zero_right]

 theorem gram_range_closure : (gram A).range.topologicalClosure = A.kerᗮ := by
  rw [← gram_range_orthogonal A]
  exact (Submodule.orthogonal_orthogonal_eq_closure _).symm

 theorem approximate_identifiable (g : G) (hg : g ∈ A.kerᗮ)
    (eps : ℝ) (heps : 0 < eps) :
    ∃ w : G, ‖g-gram A w‖ < eps := by
  rw [← gram_range_closure A] at hg
  have hc : g ∈ closure ((gram A).range : Set G) := hg
  obtain ⟨y, hy, hdist⟩ := Metric.mem_closure_iff.mp hc eps heps
  obtain ⟨w, rfl⟩ := hy
  exact ⟨w, by simpa only [dist_eq_norm, ContinuousLinearMap.coe_coe] using hdist⟩

 theorem source_approximation_bound (lam : ℝ) (hlam : 0 < lam) (g w : G) :
    ‖regularized A lam hlam (A g)-g‖ ≤ ‖g-gram A w‖ + lam*‖w‖ := by
  have he : regularized A lam hlam (A g)-g =
      (regularized A lam hlam (A (g-gram A w))-(g-gram A w))+
      (regularized A lam hlam (A (gram A w))-gram A w) := by
    simp only [map_sub]
    abel
  rw [he]
  exact (norm_add_le _ _).trans (add_le_add
    (bias_bound A lam hlam (g-gram A w))
    (source_condition_bias_bound A lam hlam w))

 theorem projected_source_approximation_bound (lam : ℝ) (hlam : 0 < lam) (g w : G) :
    ‖regularized A lam hlam (A g)-A.kerᗮ.starProjection g‖ ≤
      ‖A.kerᗮ.starProjection g-gram A w‖ + lam*‖w‖ := by
  rw [← source_projection_image A g]
  exact source_approximation_bound A lam hlam (A.kerᗮ.starProjection g) w

 theorem projected_bias_bound (lam : ℝ) (hlam : 0 < lam) (g : G) :
    ‖regularized A lam hlam (A g)-A.kerᗮ.starProjection g‖ ≤ ‖g‖ := by
  calc
    _ = ‖regularized A lam hlam (A (A.kerᗮ.starProjection g))-
        A.kerᗮ.starProjection g‖ := by rw [source_projection_image]
    _ ≤ ‖A.kerᗮ.starProjection g‖ := bias_bound A lam hlam _
    _ ≤ ‖g‖ := A.kerᗮ.norm_starProjection_apply_le g

end Komorebi.SufficientResolution.TikhonovDensity
