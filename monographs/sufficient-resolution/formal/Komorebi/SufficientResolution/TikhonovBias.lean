import Komorebi.SufficientResolution.TikhonovBounds
import Komorebi.SufficientResolution.MinimumNormReconstruction
import Komorebi.SufficientResolution.HilbertConditioning

/-!
# Bias, noise, and source-kernel ambiguity

Bias and propagated noise are not assumed orthogonal. Only their combined
identifiable error is orthogonal to the unobservable source-kernel component.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.TikhonovBias

open TikhonovConstruction TikhonovOptimality TikhonovBounds
open MinimumNormReconstruction HilbertConditioning

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V) (lam : ℝ)

 theorem filter_decomposition (hlam : 0 < lam) (g : G) :
    regularized A lam hlam (A g)+lam • resolvent A lam hlam g = g := by
  have h := resolvent_normal A lam hlam g
  simpa only [normal_apply, map_add, map_smul, regularized, ContinuousLinearMap.comp_apply] using h

 theorem bias_identity (hlam : 0 < lam) (g : G) :
    regularized A lam hlam (A g)-g = -(lam • resolvent A lam hlam g) := by
  have h := filter_decomposition A lam hlam g
  calc
    _ = regularized A lam hlam (A g) -
      (regularized A lam hlam (A g)+lam • resolvent A lam hlam g) := by rw [h]
    _ = _ := by abel

 theorem noisy_error_identity (hlam : 0 < lam) (g : G) (e : V) :
    regularized A lam hlam (A g+e)-g =
      -(lam • resolvent A lam hlam g)+regularized A lam hlam e := by
  rw [map_add, ← bias_identity A lam hlam g]
  abel

 theorem resolvent_preserves_identifiable (hlam : 0 < lam) (g : G) (hg : g ∈ A.kerᗮ) :
    resolvent A lam hlam g ∈ A.kerᗮ := by
  intro k hk
  have he := congrArg (fun x : G => inner ℝ x k) (normal_resolvent A lam hlam g)
  rw [normal_inner] at he
  change A k = 0 at hk
  rw [hk, inner_zero_right, zero_add, inner_eq_zero_symm.mpr (hg _ hk)] at he
  exact inner_eq_zero_symm.mp ((mul_eq_zero.mp he).resolve_left hlam.ne')

 theorem noisy_source_error_squared (hlam : 0 < lam) (g : G) (e : V) :
    ‖regularized A lam hlam (A g+e)-g‖^2 =
      ‖-(lam • resolvent A lam hlam (A.kerᗮ.starProjection g))+
        regularized A lam hlam e‖^2 + ‖A.ker.starProjection g‖^2 := by
  let p := A.kerᗮ.starProjection g
  let x := regularized A lam hlam (A g+e)
  have hx : x ∈ A.kerᗮ := source_kernel_orthogonal A lam hlam (A g+e)
  have hp : p ∈ A.kerᗮ := A.kerᗮ.starProjection_apply_mem g
  have ho : inner ℝ (x-p) (-(A.ker.starProjection g)) = 0 := by
    rw [inner_neg_right]
    exact neg_eq_zero.mpr (inner_eq_zero_symm.mpr
      ((A.kerᗮ.sub_mem hx hp) _ (A.ker.starProjection_apply_mem g)))
  have hs := norm_add_sq_eq_norm_sq_add_norm_sq_of_inner_eq_zero (x-p) (-(A.ker.starProjection g)) ho
  have hd : (x-p)+(-(A.ker.starProjection g)) = x-g := by
    dsimp [p]
    rw [Submodule.starProjection_orthogonal_val]
    abel
  have he : x-p = -(lam • resolvent A lam hlam p)+regularized A lam hlam e := by
    dsimp [x]
    rw [← source_projection_image A g]
    exact noisy_error_identity A lam hlam p e
  rw [hd] at hs
  rw [he, norm_neg] at hs
  simpa only [x, p, pow_two] using hs

 theorem bias_bound (hlam : 0 < lam) (g : G) :
    ‖regularized A lam hlam (A g)-g‖ ≤ ‖g‖ := by
  rw [bias_identity, norm_neg, norm_smul, Real.norm_eq_abs, abs_of_pos hlam]
  calc
    lam*‖resolvent A lam hlam g‖ ≤ lam*(‖g‖/lam) :=
      mul_le_mul_of_nonneg_left (resolvent_bound A lam hlam g) hlam.le
    _ = ‖g‖ := by field_simp

 theorem identifiable_resolvent_bound (hlam : 0 < lam)
    (alpha : ℝ) (ha : 0 < alpha) (hc : CoerciveOffKernel A alpha)
    (g : G) (hg : g ∈ A.kerᗮ) :
    ‖resolvent A lam hlam g‖ ≤ ‖g‖/(alpha^2+lam) := by
  have hp : 0 < alpha^2+lam := by positivity
  apply (le_div_iff₀ hp).mpr
  let x := resolvent A lam hlam g
  have hx := resolvent_preserves_identifiable A lam hlam g hg
  have hb := hc x hx
  have hs : (alpha*‖x‖)^2 ≤ ‖A x‖^2 :=
    (sq_le_sq₀ (mul_nonneg ha.le (norm_nonneg x)) (norm_nonneg _)).mpr hb
  have he := normal_energy A lam x
  have hn : normal A lam x = g := normal_resolvent A lam hlam g
  rw [hn] at he
  have hi := real_inner_le_norm g x
  by_cases hzero : x = 0
  · change ‖x‖ * (alpha^2+lam) ≤ ‖g‖
    rw [hzero, norm_zero, zero_mul]
    exact norm_nonneg g
  · have hpos := norm_pos_iff.mpr hzero
    change ‖x‖*(alpha^2+lam) ≤ ‖g‖
    nlinarith

 theorem identifiable_bias_bound (hlam : 0 < lam)
    (alpha : ℝ) (ha : 0 < alpha) (hc : CoerciveOffKernel A alpha)
    (g : G) (hg : g ∈ A.kerᗮ) :
    ‖regularized A lam hlam (A g)-g‖ ≤ lam/(alpha^2+lam)*‖g‖ := by
  rw [bias_identity, norm_neg, norm_smul, Real.norm_eq_abs, abs_of_pos hlam]
  calc
    lam*‖resolvent A lam hlam g‖ ≤ lam*(‖g‖/(alpha^2+lam)) :=
      mul_le_mul_of_nonneg_left (identifiable_resolvent_bound A lam hlam alpha ha hc g hg) hlam.le
    _ = _ := by ring

 theorem conditioned_bias_noise_bound (hlam : 0 < lam)
    (alpha : ℝ) (ha : 0 < alpha) (hc : CoerciveOffKernel A alpha)
    (g : G) (hg : g ∈ A.kerᗮ) (e : V) :
    ‖regularized A lam hlam (A g+e)-g‖ ≤
      lam/(alpha^2+lam)*‖g‖ + ‖e‖/(2*Real.sqrt lam) := by
  have he : regularized A lam hlam (A g+e)-g =
      (regularized A lam hlam (A g)-g)+regularized A lam hlam e := by rw [map_add]; abel
  rw [he]
  exact (norm_add_le _ _).trans (add_le_add
    (identifiable_bias_bound A lam hlam alpha ha hc g hg) (regularized_bound A lam hlam e))

 theorem full_conditioned_error_squared (hlam : 0 < lam)
    (alpha : ℝ) (ha : 0 < alpha) (hc : CoerciveOffKernel A alpha) (g : G) (e : V) :
    ‖regularized A lam hlam (A g+e)-g‖^2 ≤
      (lam/(alpha^2+lam)*‖A.kerᗮ.starProjection g‖ + ‖e‖/(2*Real.sqrt lam))^2+
        ‖A.ker.starProjection g‖^2 := by
  rw [noisy_source_error_squared]
  have hb := conditioned_bias_noise_bound A lam hlam alpha ha hc
    (A.kerᗮ.starProjection g) (A.kerᗮ.starProjection_apply_mem g) e
  rw [noisy_error_identity] at hb
  exact add_le_add ((sq_le_sq₀ (norm_nonneg _) (by positivity)).mpr hb) le_rfl

 theorem source_filter_bound (hlam : 0 < lam) (g : G) :
    ‖regularized A lam hlam (A g)‖ ≤ ‖g‖ := by
  let x := regularized A lam hlam (A g)
  let y := g-x
  have he := normal_equation_expanded A lam hlam (A g)
  have hn : A.adjoint (A y) = lam • x := by
    dsimp [y]
    rw [map_sub, map_sub]
    change A.adjoint (A g)-A.adjoint (A x) = lam • x
    change A.adjoint (A x-A g)+lam • x = 0 at he
    rw [map_sub] at he
    have hh : A.adjoint (A x)+lam • x = A.adjoint (A g) := by
      apply sub_eq_zero.mp
      convert he using 1; abel
    rw [← hh]
    abel
  have hi := congrArg (fun z : G => inner ℝ z y) hn
  rw [ContinuousLinearMap.adjoint_inner_left, real_inner_self_eq_norm_sq,
    real_inner_smul_left] at hi
  have hxy : 0 ≤ inner ℝ x y := by nlinarith [sq_nonneg ‖A y‖]
  have hs := norm_add_sq_real x y
  have hs' : x+y=g := by dsimp [y]; abel
  rw [hs'] at hs
  apply (sq_le_sq₀ (norm_nonneg x) (norm_nonneg g)).mp
  nlinarith [sq_nonneg ‖y‖]

 theorem source_condition_bias_bound (hlam : 0 < lam) (w : G) :
    ‖regularized A lam hlam (A (A.adjoint (A w)))-A.adjoint (A w)‖ ≤ lam*‖w‖ := by
  rw [bias_identity, norm_neg, norm_smul, Real.norm_eq_abs, abs_of_pos hlam]
  change lam * ‖regularized A lam hlam (A w)‖ ≤ lam * ‖w‖
  exact mul_le_mul_of_nonneg_left (source_filter_bound A lam hlam w) hlam.le

 theorem source_condition_noise_bound (hlam : 0 < lam) (w : G) (e : V) :
    ‖regularized A lam hlam (A (A.adjoint (A w))+e)-A.adjoint (A w)‖ ≤
      lam*‖w‖ + ‖e‖/(2*Real.sqrt lam) := by
  have he : regularized A lam hlam (A (A.adjoint (A w))+e)-A.adjoint (A w) =
      (regularized A lam hlam (A (A.adjoint (A w)))-A.adjoint (A w))+
        regularized A lam hlam e := by rw [map_add]; abel
  rw [he]
  exact (norm_add_le _ _).trans (add_le_add (source_condition_bias_bound A lam hlam w)
    (regularized_bound A lam hlam e))

end Komorebi.SufficientResolution.TikhonovBias
