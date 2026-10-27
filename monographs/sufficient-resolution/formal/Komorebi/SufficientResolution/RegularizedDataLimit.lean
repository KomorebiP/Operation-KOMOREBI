import Komorebi.SufficientResolution.TikhonovConvergence

/-!
# Data-space convergence and nonclosed realization boundaries

Predicted data converge to the projection on the CLOSURE of range(A). This does
not promote approximate realizability to actual realizability.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.RegularizedDataLimit

open TikhonovConstruction TikhonovBounds TikhonovConvergence
open Filter Topology

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

 theorem fitted_adjoint_identity (lam : ℝ) (hlam : 0 < lam) (v : V) :
    A (regularized A lam hlam v) = regularized A.adjoint lam hlam (A.adjoint v) := by
  apply (normal_equation_iff A.adjoint lam hlam (A.adjoint v) _).mp
  have he := congrArg A (normal_equation A lam hlam v)
  simpa only [normal_apply, ContinuousLinearMap.adjoint_adjoint, map_add, map_smul] using he

 theorem identifiable_data_eq_closure : A.adjoint.kerᗮ = A.range.topologicalClosure := by
  rw [← A.orthogonal_range]
  exact Submodule.orthogonal_orthogonal_eq_closure _

 theorem fitted_data_tendsto {ι : Type*} (f : Filter ι) (lam : ι → ℝ)
    (hlam : ∀ i, 0 < lam i) (hlim : Tendsto lam f (𝓝 0)) (v : V) :
    Tendsto (fun i => A (regularized A (lam i) (hlam i) v)) f
      (𝓝 (A.range.topologicalClosure.starProjection v)) := by
  have h := tendsto_source A.adjoint f lam hlam hlim v
  simpa only [fitted_adjoint_identity, identifiable_data_eq_closure] using h

 theorem fitted_residual_tendsto {ι : Type*} (f : Filter ι) (lam : ι → ℝ)
    (hlam : ∀ i, 0 < lam i) (hlim : Tendsto lam f (𝓝 0)) (v : V) :
    Tendsto (fun i => ‖v-A (regularized A (lam i) (hlam i) v)‖) f
      (𝓝 ‖v-A.range.topologicalClosure.starProjection v‖) :=
  (tendsto_const_nhds.sub (fitted_data_tendsto A f lam hlam hlim v)).norm

 theorem fitted_noise_tendsto_zero {ι : Type*} (f : Filter ι) (lam : ι → ℝ)
    (hlam : ∀ i, 0 < lam i) (e : ι → V) (he : Tendsto e f (𝓝 0)) :
    Tendsto (fun i => A (regularized A (lam i) (hlam i) (e i))) f (𝓝 0) := by
  apply squeeze_zero_norm (fun i => fitted_data_bound A (lam i) (hlam i) (e i))
  simpa only [norm_zero] using he.norm

 theorem noisy_fitted_data_tendsto {ι : Type*} (f : Filter ι) (lam : ι → ℝ)
    (hlam : ∀ i, 0 < lam i) (hlim : Tendsto lam f (𝓝 0))
    (v : V) (e : ι → V) (he : Tendsto e f (𝓝 0)) :
    Tendsto (fun i => A (regularized A (lam i) (hlam i) (v+e i))) f
      (𝓝 (A.range.topologicalClosure.starProjection v)) := by
  simpa only [map_add, add_zero] using
    (fitted_data_tendsto A f lam hlam hlim v).add
      (fitted_noise_tendsto_zero A f lam hlam e he)

 theorem approximately_realizable_fitted_limit {ι : Type*} (f : Filter ι)
    (lam : ι → ℝ) (hlam : ∀ i, 0 < lam i) (hlim : Tendsto lam f (𝓝 0))
    (v : V) (hv : v ∈ A.range.topologicalClosure) :
    Tendsto (fun i => A (regularized A (lam i) (hlam i) v)) f (𝓝 v) := by
  simpa only [Submodule.starProjection_eq_self_iff.mpr hv] using
    fitted_data_tendsto A f lam hlam hlim v

 theorem unrealizable_no_source_limit {ι : Type*} (f : Filter ι) [NeBot f]
    (lam : ι → ℝ) (hlam : ∀ i, 0 < lam i) (hlim : Tendsto lam f (𝓝 0))
    (v : V) (hv : v ∈ A.range.topologicalClosure) (hn : v ∉ A.range) :
    ¬ ∃ g : G, Tendsto (fun i => regularized A (lam i) (hlam i) v) f (𝓝 g) := by
  rintro ⟨g, hg⟩
  have hAg := A.continuous.continuousAt.tendsto.comp hg
  have hid := approximately_realizable_fitted_limit A f lam hlam hlim v hv
  have he : A g = v := tendsto_nhds_unique hAg hid
  exact hn ⟨g, he⟩

end Komorebi.SufficientResolution.RegularizedDataLimit
