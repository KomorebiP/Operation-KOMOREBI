import Komorebi.SufficientResolution.TikhonovConvergence

/-!
# Noisy-data and inexact-solver consistency

The parameter tends to zero and the amplified noise tends to zero separately.
The theorem uses actual constructed regularizers and actual normal residuals.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.NoisyRegularization

open TikhonovConstruction TikhonovBounds TikhonovConvergence
open Filter Topology

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

 theorem propagated_noise_tendsto_zero {ι : Type*} (f : Filter ι) (lam : ι → ℝ)
    (hlam : ∀ i, 0 < lam i) (e : ι → V)
    (hnoise : Tendsto (fun i => ‖e i‖ / Real.sqrt (lam i)) f (𝓝 0)) :
    Tendsto (fun i => regularized A (lam i) (hlam i) (e i)) f (𝓝 0) := by
  have hb : Tendsto (fun i => ‖e i‖/(2*Real.sqrt (lam i))) f (𝓝 0) := by
    convert hnoise.div_const 2 using 1 <;> simp only [zero_div, div_div, mul_comm]
  exact squeeze_zero_norm (fun i => regularized_bound A (lam i) (hlam i) (e i)) hb

 theorem noisy_source_tendsto {ι : Type*} (f : Filter ι) (lam : ι → ℝ)
    (hlam : ∀ i, 0 < lam i) (hlim : Tendsto lam f (𝓝 0)) (g : G) (e : ι → V)
    (hnoise : Tendsto (fun i => ‖e i‖ / Real.sqrt (lam i)) f (𝓝 0)) :
    Tendsto (fun i => regularized A (lam i) (hlam i) (A g+e i)) f
      (𝓝 (A.kerᗮ.starProjection g)) := by
  simpa only [map_add, add_zero] using
    (tendsto_source A f lam hlam hlim g).add
      (propagated_noise_tendsto_zero A f lam hlam e hnoise)

 theorem noisy_error_norm_tendsto {ι : Type*} (f : Filter ι) (lam : ι → ℝ)
    (hlam : ∀ i, 0 < lam i) (hlim : Tendsto lam f (𝓝 0)) (g : G) (e : ι → V)
    (hnoise : Tendsto (fun i => ‖e i‖ / Real.sqrt (lam i)) f (𝓝 0)) :
    Tendsto (fun i => ‖regularized A (lam i) (hlam i) (A g+e i)-g‖) f
      (𝓝 ‖A.ker.starProjection g‖) := by
  have ht := ((noisy_source_tendsto A f lam hlam hlim g e hnoise).sub (tendsto_const_nhds (x := g))).norm
  have he : A.kerᗮ.starProjection g-g = -(A.ker.starProjection g) := by
    rw [Submodule.starProjection_orthogonal_val]; abel
  simpa only [he, norm_neg] using ht

 theorem solver_error_tendsto_zero {ι : Type*} (f : Filter ι) (lam : ι → ℝ)
    (hlam : ∀ i, 0 < lam i) (v : ι → V) (x : ι → G)
    (hsolver : Tendsto (fun i => ‖normal A (lam i) (x i)-A.adjoint (v i)‖/(lam i))
      f (𝓝 0)) :
    Tendsto (fun i => x i-regularized A (lam i) (hlam i) (v i)) f (𝓝 0) := by
  apply squeeze_zero_norm _ hsolver
  intro i
  exact approximate_solver_bound A (lam i) (hlam i) (v i) (x i)

 theorem noisy_inexact_solver_tendsto {ι : Type*} (f : Filter ι) (lam : ι → ℝ)
    (hlam : ∀ i, 0 < lam i) (hlim : Tendsto lam f (𝓝 0))
    (g : G) (e : ι → V) (x : ι → G)
    (hnoise : Tendsto (fun i => ‖e i‖ / Real.sqrt (lam i)) f (𝓝 0))
    (hsolver : Tendsto (fun i => ‖normal A (lam i) (x i)-A.adjoint (A g+e i)‖/(lam i))
      f (𝓝 0)) : Tendsto x f (𝓝 (A.kerᗮ.starProjection g)) := by
  have h := (solver_error_tendsto_zero A f lam hlam (fun i => A g+e i) x hsolver).add
    (noisy_source_tendsto A f lam hlam hlim g e hnoise)
  simpa only [sub_add_cancel, zero_add] using h

omit [InnerProductSpace ℝ V] [CompleteSpace V] in
 theorem envelope_noise_tendsto_zero {ι : Type*} (f : Filter ι) (lam : ι → ℝ)
    (e : ι → V) (eta : ι → ℝ)
    (he : ∀ i, ‖e i‖ ≤ eta i)
    (heta : Tendsto (fun i => eta i/Real.sqrt (lam i)) f (𝓝 0)) :
    Tendsto (fun i => ‖e i‖/Real.sqrt (lam i)) f (𝓝 0) := by
  apply squeeze_zero (fun i => div_nonneg (norm_nonneg _) (Real.sqrt_nonneg _)) _ heta
  intro i
  exact div_le_div_of_nonneg_right (he i) (Real.sqrt_nonneg _)

 theorem square_schedule_consistent {ι : Type*} (f : Filter ι) (s : ι → ℝ)
    (hs : ∀ i, 0 < s i) (hlim : Tendsto s f (𝓝 0)) (g : G) (e : ι → V)
    (he : ∀ i, ‖e i‖ ≤ (s i)^2) :
    Tendsto (fun i => regularized A ((s i)^2) (sq_pos_of_pos (hs i)) (A g+e i)) f
      (𝓝 (A.kerᗮ.starProjection g)) := by
  apply noisy_source_tendsto A f (fun i => (s i)^2) (fun i => sq_pos_of_pos (hs i))
    (by simpa only [zero_pow (by decide : (2 : ℕ) ≠ 0)] using hlim.pow 2) g e
  apply squeeze_zero (fun i => div_nonneg (norm_nonneg _) (Real.sqrt_nonneg _)) _ hlim
  intro i
  rw [Real.sqrt_sq (hs i).le]
  apply (div_le_iff₀ (hs i)).mpr
  simpa only [pow_two] using he i

end Komorebi.SufficientResolution.NoisyRegularization
