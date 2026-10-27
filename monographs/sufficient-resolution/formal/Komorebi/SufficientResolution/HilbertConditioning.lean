import Komorebi.SufficientResolution.HilbertGlobalization
import Mathlib.Analysis.Normed.Module.FiniteDimension
import Mathlib.Tactic.GCongr

/-!
# Conditioning-aware globalization estimates

The compatibility residual controls the inconsistent component only under an
explicit lower norm bound away from the kernel. The obstruction term remains.
Finite dimension supplies some positive constant, not a computed singular value
and not a uniform constant over a family of changing operators.
-/

set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.HilbertConditioning

open OrthogonalResolution

variable {V W : Type*}
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V]
variable [NormedAddCommGroup W] [NormedSpace ℝ W]
variable (delta : V →L[ℝ] W)

/-- A supplied whole-map coercivity bound on the orthogonal complement of the kernel. -/
def CoerciveOffKernel (sigma : ℝ) : Prop :=
  ∀ x : V, x ∈ delta.kerᗮ → sigma * ‖x‖ ≤ ‖delta x‖

/-- Finite dimension supplies a positive conditioning constant, including a zero complement. -/
 theorem exists_coercivity_finite [FiniteDimensional ℝ V] :
    ∃ sigma : ℝ, 0 < sigma ∧ CoerciveOffKernel delta sigma := by
  let f : delta.kerᗮ →ₗ[ℝ] W := delta.toLinearMap.comp delta.kerᗮ.subtype
  have hf : Function.Injective f := by
    apply LinearMap.ker_eq_bot.mp
    apply le_antisymm
    · intro x hx
      change f x = 0 at hx
      have hk : (x : V) ∈ delta.ker := hx
      have ho := x.2
      have hi : inner ℝ (x : V) (x : V) = 0 := ho _ hk
      have hz : (x : V) = 0 := inner_self_eq_zero.mp hi
      simpa only [Submodule.mem_bot] using (Subtype.ext hz : x = 0)
    · exact bot_le
  obtain ⟨c, hc, hanti⟩ := f.injective_iff_antilipschitz.mp hf
  have hcR : 0 < (c : ℝ) := hc
  refine ⟨(c : ℝ)⁻¹, inv_pos.mpr hcR, ?_⟩
  intro x hx
  have hb := hanti.le_mul_dist ⟨x, hx⟩ 0
  rw [dist_eq_norm, dist_eq_norm] at hb
  simp only [sub_zero, map_zero, f, LinearMap.comp_apply,
    Submodule.subtype_apply, ContinuousLinearMap.coe_coe] at hb
  calc
    (c : ℝ)⁻¹ * ‖x‖ ≤ (c : ℝ)⁻¹ * ((c : ℝ) * ‖delta x‖) :=
      mul_le_mul_of_nonneg_left hb (inv_nonneg.mpr hcR.le)
    _ = ‖delta x‖ := by rw [← mul_assoc, inv_mul_cancel₀ hcR.ne', one_mul]

variable [delta.ker.HasOrthogonalProjection]

 theorem inconsistency_residual (v : V) :
    delta (inconsistency delta.ker v) = delta v := by
  change delta (v - delta.ker.starProjection v) = delta v
  rw [map_sub, show delta (delta.ker.starProjection v) = 0 from
    delta.ker.starProjection_apply_mem v, sub_zero]

 theorem inconsistency_le_residual (sigma : ℝ) (hs : 0 < sigma)
    (hc : CoerciveOffKernel delta sigma) (v : V) :
    ‖inconsistency delta.ker v‖ ≤ ‖delta v‖ / sigma := by
  apply (le_div_iff₀ hs).mpr
  have hb := hc _ (inconsistency_mem delta.ker v)
  rw [inconsistency_residual] at hb
  nlinarith

variable (R : Submodule ℝ V) [R.HasOrthogonalProjection]

 theorem conditioned_distance_sq (hR : R ≤ delta.ker) (sigma : ℝ) (hs : 0 < sigma)
    (hc : CoerciveOffKernel delta sigma) (v : V) :
    Metric.infDist v (R : Set V) ^ 2 ≤
      ‖obstruction R delta.ker v‖ ^ 2 + (‖delta v‖ / sigma) ^ 2 := by
  rw [infDist_sq_decomposition R delta.ker hR v]
  have hi := inconsistency_le_residual delta sigma hs hc v
  have hn := div_nonneg (norm_nonneg (delta v)) hs.le
  exact add_le_add le_rfl ((sq_le_sq₀ (norm_nonneg _) hn).mpr hi)

 theorem obstruction_lower_bound (hR : R ≤ delta.ker) (v : V) :
    ‖obstruction R delta.ker v‖ ≤ Metric.infDist v (R : Set V) := by
  have hp := infDist_sq_decomposition R delta.ker hR v
  nlinarith [sq_nonneg ‖inconsistency delta.ker v‖,
    norm_nonneg (obstruction R delta.ker v), Metric.infDist_nonneg (x := v) (s := (R : Set V))]

 theorem compatible_distance (v : V) (hv : delta v = 0) :
    Metric.infDist v (R : Set V) = ‖obstruction R delta.ker v‖ := by
  rw [infDist_eq_error, error_split R delta.ker,
    (inconsistency_zero_iff delta.ker v).mpr hv, add_zero]

 theorem tolerance_distance_sq (hR : R ≤ delta.ker) (sigma : ℝ) (hs : 0 < sigma)
    (hc : CoerciveOffKernel delta sigma) (v : V) (eta epsilon : ℝ)
    (ho : ‖obstruction R delta.ker v‖ ≤ eta) (hd : ‖delta v‖ ≤ epsilon) :
    Metric.infDist v (R : Set V) ^ 2 ≤ eta ^ 2 + (epsilon / sigma) ^ 2 := by
  apply (conditioned_distance_sq delta R hR sigma hs hc v).trans
  have heta : 0 ≤ eta := (norm_nonneg _).trans ho
  have heps : 0 ≤ epsilon := (norm_nonneg _).trans hd
  gcongr

 theorem tolerance_distance (sigma : ℝ) (hs : 0 < sigma)
    (hc : CoerciveOffKernel delta sigma) (v : V) (eta epsilon : ℝ)
    (ho : ‖obstruction R delta.ker v‖ ≤ eta) (hd : ‖delta v‖ ≤ epsilon) :
    Metric.infDist v (R : Set V) ≤ eta + epsilon / sigma := by
  rw [infDist_eq_error, error_split R delta.ker]
  apply (norm_add_le _ _).trans
  exact add_le_add ho ((inconsistency_le_residual delta sigma hs hc v).trans
    ((div_le_div_iff_of_pos_right hs).mpr hd))

/-- Dropping the obstruction requires an explicit vanishing hypothesis. -/
 theorem distance_le_residual_of_no_obstruction (sigma : ℝ) (hs : 0 < sigma)
    (hc : CoerciveOffKernel delta sigma) (v : V)
    (ho : obstruction R delta.ker v = 0) :
    Metric.infDist v (R : Set V) ≤ ‖delta v‖ / sigma := by
  rw [infDist_eq_error, error_split R delta.ker, ho, zero_add]
  exact inconsistency_le_residual delta sigma hs hc v

 theorem distance_le_residual_of_exact (hR : R = delta.ker) (sigma : ℝ) (hs : 0 < sigma)
    (hc : CoerciveOffKernel delta sigma) (v : V) :
    Metric.infDist v (R : Set V) ≤ ‖delta v‖ / sigma := by
  apply distance_le_residual_of_no_obstruction delta R sigma hs hc v
  subst R
  simp [obstruction]

omit [delta.ker.HasOrthogonalProjection] in
/-- Residual-only reconstruction for every vector forces exactness of the presentation. -/
 theorem exact_of_residual_distance_bound (hR : R ≤ delta.ker) (c : ℝ)
    (hb : ∀ v : V, Metric.infDist v (R : Set V) ≤ c * ‖delta v‖) :
    R = delta.ker := by
  apply le_antisymm hR
  intro v hv
  have he := hb v
  change delta v = 0 at hv
  rw [infDist_eq_error, hv, norm_zero, mul_zero] at he
  have hz := norm_eq_zero.mp (le_antisymm he (norm_nonneg _))
  exact Submodule.starProjection_eq_self_iff.mp (sub_eq_zero.mp hz).symm


end Komorebi.SufficientResolution.HilbertConditioning
