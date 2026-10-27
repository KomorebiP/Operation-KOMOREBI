import KomorebiSpace.ResidualPerturbation
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Tactic.Ring

set_option autoImplicit false

/-!
# Controlled motion of actual exact spaces

Two independently certified residual bounds control both directions of kernel
motion. Unlike the previous preserved-kernel theorem, neither kernel inclusion
is assumed. The comparison is between the actual orthogonal projections. The
operator-norm estimate uses the larger directional gain, not their sum.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace MovingKernel
open HilbertKernelProjection
variable {E : Type u} {R : Type v}
variable [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
variable [NormedAddCommGroup R] [NormedSpace ℝ R]
variable (d e : E →L[ℝ] R)

/-- A bound on old exact vectors also controls projection of new-orthogonal vectors. -/
theorem complement_projection_bound {β : ℝ} (hβ : 0 ≤ β)
    (h : ∀ z, d z = 0 → ‖z-projection e z‖ ≤ β*‖z‖)
    (u : E) (hu : u ∈ e.kerᗮ) :
    ‖projection d u‖ ≤ β*‖u‖ := by
  let v := projection d u
  have hv : d v = 0 := projection_exact d u
  have h1 : inner ℝ v (u-v) = 0 := error_orthogonal d u v hv
  have h2 : inner ℝ (projection e v) u = 0 := hu _ (projection_mem e v)
  have hid : inner ℝ (v-projection e v) u = ‖v‖^2 := by
    rw [inner_sub_left, h2, sub_zero]
    rw [inner_sub_right, real_inner_self_eq_norm_sq] at h1
    linarith
  have hc : ‖v‖^2 ≤ (β*‖v‖)*‖u‖ := by
    calc
      ‖v‖^2 = inner ℝ (v-projection e v) u := hid.symm
      _ ≤ ‖v-projection e v‖*‖u‖ := real_inner_le_norm _ _
      _ ≤ (β*‖v‖)*‖u‖ := mul_le_mul_of_nonneg_right (h v hv) (norm_nonneg u)
  by_cases hz : ‖v‖ = 0
  · change ‖v‖ ≤ _
    rw [hz]
    positivity
  · have hp : 0 < ‖v‖ := lt_of_le_of_ne (norm_nonneg v) (Ne.symm hz)
    change ‖v‖ ≤ _
    nlinarith

/-- The two components of projection motion are orthogonal, hence a maximum bound. -/
theorem projection_motion_of_directional {α β : ℝ} (hα : 0 ≤ α) (hβ : 0 ≤ β)
    (hnew : ∀ z, e z = 0 → ‖z-projection d z‖ ≤ α*‖z‖)
    (hold : ∀ z, d z = 0 → ‖z-projection e z‖ ≤ β*‖z‖)
    (x : E) :
    ‖projection d x-projection e x‖ ≤ max α β * ‖x‖ := by
  let u := x-projection e x
  let v := projection e x
  let w := projection d u
  let z := v-projection d v
  have hu : u ∈ e.kerᗮ := error_orthogonal e x
  have hv : e v = 0 := projection_exact e x
  have hw : d w = 0 := projection_exact d u
  have hz : z ∈ d.kerᗮ := error_orthogonal d v
  have horth : inner ℝ w z = 0 := hz w hw
  have huv : inner ℝ u v = 0 := by
    rw [real_inner_comm]
    exact hu v hv
  have hid : projection d x-projection e x = w-z := by
    dsimp [w,z,u,v]
    rw [map_sub]
    abel
  have hxid : x = u+v := by dsimp [u,v]; abel
  have hsq : ‖projection d x-projection e x‖^2 = ‖w‖^2+‖z‖^2 := by
    rw [hid,norm_sub_sq_real,horth]
    ring
  have hxnorm : ‖x‖^2 = ‖u‖^2+‖v‖^2 := by
    rw [hxid,norm_add_sq_real,huv]
    ring
  have hwu : ‖w‖ ≤ max α β * ‖u‖ :=
    (complement_projection_bound d e hβ hold u hu).trans
      (mul_le_mul_of_nonneg_right (le_max_right α β) (norm_nonneg u))
  have hzv : ‖z‖ ≤ max α β * ‖v‖ :=
    (hnew v hv).trans
      (mul_le_mul_of_nonneg_right (le_max_left α β) (norm_nonneg v))
  have hm : 0 ≤ max α β := le_trans hα (le_max_left α β)
  have hw2 := (sq_le_sq₀ (norm_nonneg w) (mul_nonneg hm (norm_nonneg u))).mpr hwu
  have hz2 := (sq_le_sq₀ (norm_nonneg z) (mul_nonneg hm (norm_nonneg v))).mpr hzv
  apply (sq_le_sq₀ (norm_nonneg _) (mul_nonneg hm (norm_nonneg x))).mp
  rw [hsq,mul_pow,hxnorm]
  rw [mul_pow] at hw2 hz2
  nlinarith

/-- Two residual certificates control motion without preserving the old kernel. -/
theorem projection_motion (B : ResidualRobustness.Bound d)
    (B' : ResidualRobustness.Bound e) {ε : ℝ} (hε : 0 ≤ ε)
    (he : ∀ x, ‖(d-e) x‖ ≤ ε*‖x‖) (x : E) :
    ‖projection d x-projection e x‖ ≤ max B.constant B'.constant * ε * ‖x‖ := by
  have hrev : ∀ z, ‖(e-d) z‖ ≤ ε*‖z‖ := by
    intro z
    simpa only [sub_apply, norm_sub_rev] using he z
  have hb := projection_motion_of_directional d e
    (mul_nonneg B.nonneg hε) (mul_nonneg B'.nonneg hε)
    (fun z hz => B.new_exact_near_old e ε he z hz)
    (fun z hz => B'.new_exact_near_old d ε hrev z hz) x
  simpa only [max_mul_of_nonneg _ _ hε] using hb

/-- The comparison is an operator-norm statement, not a sampled-vector claim. -/
theorem projection_opNorm (B : ResidualRobustness.Bound d)
    (B' : ResidualRobustness.Bound e) {ε : ℝ} (he : ‖d-e‖ ≤ ε) :
    ‖projection d-projection e‖ ≤ max B.constant B'.constant * ε := by
  have hε : 0 ≤ ε := (norm_nonneg (d-e)).trans he
  apply ContinuousLinearMap.opNorm_le_bound _ (mul_nonneg
    (B.nonneg.trans (le_max_left _ _)) hε)
  intro x
  exact projection_motion d e B B' hε
    (fun z => ((d-e).le_opNorm z).trans
      (mul_le_mul_of_nonneg_right he (norm_nonneg z))) x

/-- Errors in the candidate and in the model contribute separately. -/
theorem repaired_input_motion (B : ResidualRobustness.Bound d)
    (B' : ResidualRobustness.Bound e) {ε : ℝ} (he : ‖d-e‖ ≤ ε) (x y : E) :
    ‖projection d x-projection e y‖ ≤
      ‖x-y‖ + (max B.constant B'.constant * ε)*‖y‖ := by
  calc
    _ ≤ ‖projection d x-projection d y‖ + ‖projection d y-projection e y‖ :=
      norm_sub_le_norm_sub_add_norm_sub _ _ _
    _ ≤ ‖x-y‖ + (max B.constant B'.constant * ε)*‖y‖ := by
      apply add_le_add
      · simpa only [map_sub] using projection_norm d (x-y)
      · exact ((projection d-projection e).le_opNorm y).trans
          (mul_le_mul_of_nonneg_right (projection_opNorm d e B B' he) (norm_nonneg y))

/-- Distance-to-exactness also changes by at most the projection-motion budget. -/
theorem distance_motion (B : ResidualRobustness.Bound d)
    (B' : ResidualRobustness.Bound e) {ε : ℝ} (he : ‖d-e‖ ≤ ε) (x : E) :
    |‖x-projection d x‖-‖x-projection e x‖| ≤
      (max B.constant B'.constant * ε)*‖x‖ := by
  have h := abs_norm_sub_norm_le (x-projection d x) (x-projection e x)
  have hid : (x-projection d x)-(x-projection e x)=projection e x-projection d x := by abel
  rw [hid] at h
  have hs : ‖projection e x-projection d x‖ = ‖projection d x-projection e x‖ := norm_sub_rev _ _
  rw [hs] at h
  exact h.trans (((projection d-projection e).le_opNorm x).trans
    (mul_le_mul_of_nonneg_right (projection_opNorm d e B B' he) (norm_nonneg x)))

/-- Losing a unit exact direction forces the new residual gain to blow up. -/
theorem lost_exact_unit_forces_gain (B' : ResidualRobustness.Bound e)
    {ε : ℝ} (he : ‖d-e‖ ≤ ε) (x : E) (hx : d x=0)
    (hn : ‖x‖=1) (hp : projection e x=0) : 1 ≤ B'.constant*ε := by
  have hrev : ∀ z, ‖(e-d) z‖ ≤ ε*‖z‖ := by
    intro z
    have h := ((d-e).le_opNorm z).trans
      (mul_le_mul_of_nonneg_right he (norm_nonneg z))
    simpa only [sub_apply,norm_sub_rev] using h
  have h := B'.new_exact_near_old d ε hrev x hx
  simpa only [hp,sub_zero,hn,mul_one] using h

/-- Models sharing one certified residual-gain bound. Their kernels may differ. -/
abbrev StableModel (M : NNReal) :=
  {f : E →L[ℝ] R // ∀ x, ‖x-projection f x‖ ≤ (M:ℝ)*‖f x‖}

/-- The projector is Lipschitz on each uniformly certified model class. -/
theorem projection_lipschitz (M : NNReal) :
    LipschitzWith M (fun f : StableModel (E := E) (R := R) M => projection f.val) := by
  apply LipschitzWith.of_dist_le_mul
  intro f g
  let B : ResidualRobustness.Bound f.val := ⟨M,M.property,f.property⟩
  let B' : ResidualRobustness.Bound g.val := ⟨M,M.property,g.property⟩
  have h := projection_opNorm f.val g.val B B' (le_refl ‖f.val-g.val‖)
  simpa only [B,B',max_self,Subtype.dist_eq,dist_eq_norm] using h

theorem continuous_projection (M : NNReal) :
    Continuous (fun f : StableModel (E := E) (R := R) M => projection f.val) :=
  (projection_lipschitz M).continuous

end MovingKernel
end KomorebiSpace
end
