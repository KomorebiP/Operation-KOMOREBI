import Komorebi.SufficientResolution.MinimumNormReconstruction

/-!
# Minimum norm among all least-squares sources

Every minimizer is the canonical reconstruction plus a kernel vector. The exact
Pythagorean source identity proves minimum norm and uniqueness without injecting A.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.MinimumNormOptimality

open MinimumNormReconstruction OrthogonalResolution

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V]
variable (A : G →L[ℝ] V) [CompleteSpace A.range]

 theorem recover_best_error (v : V) :
    ‖v - A (recover A v)‖ = Metric.infDist v (A.range : Set V) := by
  rw [image_recover, infDist_eq_error]
  rfl

 theorem recover_best (v : V) (g : G) :
    ‖v - A (recover A v)‖ ≤ ‖v - A g‖ := by
  rw [image_recover]
  exact best_approximation A.range v (A.mem_range_self g)

 theorem least_squares_iff (v : V) (g : G) :
    ‖v - A g‖ = Metric.infDist v (A.range : Set V) ↔
      A g = A (recover A v) := by
  rw [image_recover, infDist_eq_error]
  exact best_approximation_unique A.range v (A.mem_range_self g)

 theorem candidate_error_decomposition (v : V) (g : G) :
    ‖v - A g‖ ^ 2 = ‖v - A (recover A v)‖ ^ 2 + ‖A (g - recover A v)‖ ^ 2 := by
  rw [map_sub, norm_sub_rev (A g) (A (recover A v)), image_recover]
  exact candidate_error_sq A.range v (A.mem_range_self g)

 theorem same_image_iff_kernel (v : V) (g : G) :
    A g = A (recover A v) ↔ g - recover A v ∈ A.ker := by
  change A g = A (recover A v) ↔ A (g - recover A v) = 0
  rw [map_sub, sub_eq_zero]

 theorem all_least_squares_sources (v : V) (g : G) :
    ‖v - A g‖ = Metric.infDist v (A.range : Set V) ↔
      ∃ k : G, k ∈ A.ker ∧ g = recover A v + k := by
  rw [least_squares_iff, same_image_iff_kernel]
  constructor
  · intro hk
    exact ⟨g - recover A v, hk, by abel⟩
  · rintro ⟨k, hk, rfl⟩
    simpa only [add_sub_cancel_left] using hk

 theorem source_norm_sq (v : V) (g : G) (h : A g = A (recover A v)) :
    ‖g‖ ^ 2 = ‖recover A v‖ ^ 2 + ‖g - recover A v‖ ^ 2 := by
  have hk := (same_image_iff_kernel A v g).mp h
  have ho : inner ℝ (recover A v) (g - recover A v) = 0 :=
    inner_eq_zero_symm.mp (recover_mem A v _ hk)
  have hp := norm_add_sq_eq_norm_sq_add_norm_sq_of_inner_eq_zero _ _ ho
  simpa only [add_sub_cancel, pow_two] using hp

 theorem minimum_norm (v : V) (g : G) (h : A g = A (recover A v)) :
    ‖recover A v‖ ≤ ‖g‖ := by
  have hp := source_norm_sq A v g h
  nlinarith [sq_nonneg ‖g-recover A v‖, norm_nonneg g, norm_nonneg (recover A v)]

 theorem minimum_norm_unique (v : V) (g : G) (h : A g = A (recover A v)) :
    ‖g‖ ≤ ‖recover A v‖ ↔ g = recover A v := by
  constructor
  · intro hb
    have hp := source_norm_sq A v g h
    have hn : ‖g-recover A v‖ = 0 := by
      nlinarith [norm_nonneg g, norm_nonneg (recover A v), norm_nonneg (g-recover A v)]
    exact sub_eq_zero.mp (norm_eq_zero.mp hn)
  · rintro rfl
    exact le_rfl

/-- Unique minimum-norm source among every least-squares minimizer. -/
 theorem unique_minimum_norm_least_squares (v : V) :
    ∃! g : G, (‖v - A g‖ = Metric.infDist v (A.range : Set V)) ∧
      ∀ h : G, ‖v - A h‖ = Metric.infDist v (A.range : Set V) → ‖g‖ ≤ ‖h‖ := by
  refine ⟨recover A v, ⟨recover_best_error A v, ?_⟩, ?_⟩
  · intro h hh
    exact minimum_norm A v h ((least_squares_iff A v h).mp hh)
  · intro g hg
    exact (minimum_norm_unique A v g ((least_squares_iff A v g).mp hg.1)).mp
      (hg.2 _ (recover_best_error A v))

 theorem exact_source_recovery_iff (g : G) :
    recover A (A g) = g ↔ g ∈ A.kerᗮ := by
  rw [recover_image, Submodule.starProjection_eq_self_iff]

 theorem unidentifiable_source_error (g : G) :
    g - recover A (A g) = A.ker.starProjection g := by
  rw [recover_image, Submodule.starProjection_orthogonal_val]
  abel

/-- Observation noise and invisible source content occupy orthogonal source sectors. -/
 theorem noisy_source_error_sq (g : G) (e : V) :
    ‖recover A (A g + e) - g‖ ^ 2 =
      ‖recover A e‖ ^ 2 + ‖A.ker.starProjection g‖ ^ 2 := by
  have hk : -(A.ker.starProjection g) ∈ A.ker :=
    A.ker.neg_mem (A.ker.starProjection_apply_mem g)
  have ho : inner ℝ (recover A e) (-(A.ker.starProjection g)) = 0 :=
    inner_eq_zero_symm.mp (recover_mem A e _ hk)
  have hp := norm_add_sq_eq_norm_sq_add_norm_sq_of_inner_eq_zero _ _ ho
  have he : recover A (A g + e) - g = recover A e + -(A.ker.starProjection g) := by
    rw [map_add, recover_image, Submodule.starProjection_orthogonal_val]
    abel
  rw [he]
  simpa only [pow_two, norm_neg] using hp

end Komorebi.SufficientResolution.MinimumNormOptimality
