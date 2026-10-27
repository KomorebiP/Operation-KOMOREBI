import Komorebi.SufficientResolution.TikhonovDensity

/-!
# Strong regularization convergence without closed range

The positive parameter family is arbitrary and may be indexed by any filter.
The limit is the identifiable projection, not an inverse on invisible source data.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.TikhonovConvergence

open TikhonovConstruction TikhonovBias TikhonovDensity MinimumNormReconstruction
open Filter Topology

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

 theorem tendsto_identifiable {ι : Type*} (f : Filter ι) (lam : ι → ℝ)
    (hlam : ∀ i, 0 < lam i) (hlim : Tendsto lam f (𝓝 0))
    (g : G) (hg : g ∈ A.kerᗮ) :
    Tendsto (fun i => regularized A (lam i) (hlam i) (A g)) f (𝓝 g) := by
  apply Metric.tendsto_nhds.mpr
  intro eps heps
  obtain ⟨w, hw⟩ := approximate_identifiable A g hg (eps/2) (by positivity)
  have hcut := (tendsto_order.mp hlim).2 (eps/(2*(‖w‖+1))) (by positivity)
  filter_upwards [hcut] with i hi
  rw [dist_eq_norm]
  have hmul : lam i * (2*(‖w‖+1)) < eps :=
    (lt_div_iff₀ (by positivity)).mp hi
  have hb := source_approximation_bound A (lam i) (hlam i) g w
  have hp := hlam i
  nlinarith

 theorem tendsto_source {ι : Type*} (f : Filter ι) (lam : ι → ℝ)
    (hlam : ∀ i, 0 < lam i) (hlim : Tendsto lam f (𝓝 0)) (g : G) :
    Tendsto (fun i => regularized A (lam i) (hlam i) (A g)) f
      (𝓝 (A.kerᗮ.starProjection g)) := by
  have h := tendsto_identifiable A f lam hlam hlim (A.kerᗮ.starProjection g)
    (A.kerᗮ.starProjection_apply_mem g)
  simpa only [source_projection_image] using h

 theorem tendsto_bias_vector {ι : Type*} (f : Filter ι) (lam : ι → ℝ)
    (hlam : ∀ i, 0 < lam i) (hlim : Tendsto lam f (𝓝 0)) (g : G) :
    Tendsto (fun i => regularized A (lam i) (hlam i) (A g)-g) f
      (𝓝 (-(A.ker.starProjection g))) := by
  have h := (tendsto_source A f lam hlam hlim g).sub (tendsto_const_nhds (x := g))
  convert h using 1
  rw [Submodule.starProjection_orthogonal_val]
  congr 1
  abel

 theorem tendsto_error_norm {ι : Type*} (f : Filter ι) (lam : ι → ℝ)
    (hlam : ∀ i, 0 < lam i) (hlim : Tendsto lam f (𝓝 0)) (g : G) :
    Tendsto (fun i => ‖regularized A (lam i) (hlam i) (A g)-g‖) f
      (𝓝 ‖A.ker.starProjection g‖) := by
  simpa only [norm_neg] using (tendsto_bias_vector A f lam hlam hlim g).norm

 theorem tendsto_error_squared {ι : Type*} (f : Filter ι) (lam : ι → ℝ)
    (hlam : ∀ i, 0 < lam i) (hlim : Tendsto lam f (𝓝 0)) (g : G) :
    Tendsto (fun i => ‖regularized A (lam i) (hlam i) (A g)-g‖^2) f
      (𝓝 (‖A.ker.starProjection g‖^2)) :=
  (tendsto_error_norm A f lam hlam hlim g).pow 2

 theorem exact_limit_iff_identifiable {ι : Type*} (f : Filter ι) [NeBot f]
    (lam : ι → ℝ) (hlam : ∀ i, 0 < lam i) (hlim : Tendsto lam f (𝓝 0)) (g : G) :
    Tendsto (fun i => regularized A (lam i) (hlam i) (A g)) f (𝓝 g) ↔ g ∈ A.kerᗮ := by
  constructor
  · intro h
    have he := tendsto_nhds_unique (tendsto_source A f lam hlam hlim g) h
    exact Submodule.starProjection_eq_self_iff.mp he
  · exact tendsto_identifiable A f lam hlam hlim g

end Komorebi.SufficientResolution.TikhonovConvergence
