import Mathlib.Analysis.InnerProductSpace.Projection.Basic
import Mathlib.Analysis.Normed.Module.FiniteDimension
import Mathlib.Tactic.Abel
import Mathlib.Tactic.Positivity

set_option autoImplicit false

/-!
# Finite-dimensional kernel correction with a derived sharp gain

The correction is the orthogonal projection onto the actual kernel. The gain
is the norm of the inverse of the defect restricted to the orthogonal
complement. No lower bound, spectral gap, or right inverse is assumed.
The residual norm is the norm of the supplied target space; it need not be
an inner-product norm. These are classical finite-dimensional constructions,
not executable singular-value algorithms or uniform bounds over all maps.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace KernelProjection
variable {E : Type u} {R : Type v}
variable [NormedAddCommGroup E] [InnerProductSpace ℝ E] [FiniteDimensional ℝ E]
variable [NormedAddCommGroup R] [NormedSpace ℝ R]
variable (d : E →L[ℝ] R)

/-- Canonical for the specified inner product and the actual defect kernel. -/
def projection : E →L[ℝ] E := d.ker.starProjection

@[simp] theorem projection_mem (x : E) : projection d x ∈ d.ker :=
  d.ker.starProjection_apply_mem x

@[simp] theorem projection_exact (x : E) : d (projection d x) = 0 :=
  projection_mem d x

@[simp] theorem projection_fixes (x : E) (hx : d x = 0) : projection d x = x :=
  d.ker.starProjection_eq_self_iff.mpr hx

@[simp] theorem projection_idempotent (x : E) :
    projection d (projection d x) = projection d x :=
  projection_fixes d _ (projection_exact d x)

theorem projection_norm (x : E) : ‖projection d x‖ ≤ ‖x‖ :=
  d.ker.norm_starProjection_apply_le x

theorem projection_opNorm : ‖projection d‖ ≤ 1 := d.ker.starProjection_norm_le

theorem error_orthogonal (x : E) : x - projection d x ∈ d.kerᗮ :=
  d.ker.sub_starProjection_mem_orthogonal x

@[simp] theorem defect_error (x : E) : d (x - projection d x) = d x := by
  rw [map_sub, projection_exact, sub_zero]

theorem projection_orthogonal_zero (x : E) (hx : x ∈ d.kerᗮ) :
    projection d x = 0 := by
  change d.ker.starProjection x = 0
  exact d.ker.starProjection_apply_eq_zero_iff.mpr hx

/-- The residual map on the complementary directions has no kernel. -/
def reduced : d.kerᗮ →L[ℝ] R := d.comp d.kerᗮ.subtypeL

omit [FiniteDimensional ℝ E] in
@[simp] theorem reduced_apply (x : d.kerᗮ) : reduced d x = d x.val := rfl

omit [FiniteDimensional ℝ E] in
theorem reduced_injective : Function.Injective (reduced d) := by
  intro x y h
  apply Subtype.ext
  apply sub_eq_zero.mp
  have hk : x.val - y.val ∈ d.ker := by
    change d (x.val - y.val) = 0
    rw [map_sub]
    exact sub_eq_zero.mpr h
  have ho : x.val - y.val ∈ d.kerᗮ := d.kerᗮ.sub_mem x.property y.property
  exact inner_self_eq_zero.mp (ho _ hk)

/-- Finite dimensionality supplies continuity of this inverse on the actual range. -/
def reducedEquiv : d.kerᗮ ≃L[ℝ] LinearMap.range (reduced d).toLinearMap :=
  (LinearEquiv.ofInjective (reduced d).toLinearMap (reduced_injective d)).toContinuousLinearEquiv

@[simp] theorem reducedEquiv_value (x : d.kerᗮ) :
    (reducedEquiv d x).val = d x.val := rfl

/-- Sharp residual-to-kernel-distance gain for the supplied norms. It is zero
when the complementary space is zero; no undefined least-positive singular
value is used in that case. -/
def gain : ℝ := ‖(reducedEquiv d).symm.toContinuousLinearMap‖

theorem gain_nonneg : 0 ≤ gain d := by
  unfold gain
  exact norm_nonneg ((reducedEquiv d).symm.toContinuousLinearMap)

theorem complement_bound (x : d.kerᗮ) : ‖x.val‖ ≤ gain d * ‖d x.val‖ := by
  have hb := (reducedEquiv d).symm.toContinuousLinearMap.le_opNorm (reducedEquiv d x)
  change ‖(reducedEquiv d).symm (reducedEquiv d x)‖ ≤ gain d * ‖d x.val‖ at hb
  simpa only [ContinuousLinearEquiv.symm_apply_apply, Submodule.norm_coe] using hb


/-- The formerly assumed correction estimate is derived. -/
theorem error_bound (x : E) : ‖x - projection d x‖ ≤ gain d * ‖d x‖ := by
  have hb := complement_bound d ⟨x - projection d x, error_orthogonal d x⟩
  simpa only [defect_error] using hb

/-- Orthogonal correction minimizes anchor displacement, not necessarily a
separate global product norm after graph reconstruction. -/
theorem projection_best (x y : E) (hy : d y = 0) :
    ‖x - projection d x‖ ≤ ‖x - y‖ := by
  calc
    _ = ‖(x-y) - projection d (x-y)‖ := by
      rw [map_sub, projection_fixes d y hy]
      congr 1
      abel
    _ = ‖d.kerᗮ.starProjection (x-y)‖ := by
      rw [Submodule.starProjection_orthogonal_val]
      rfl
    _ ≤ _ := d.kerᗮ.norm_starProjection_apply_le (x-y)

/-- Characterization by the protected kernel and orthogonal displacement. -/
theorem projection_unique (x y : E) (hy : d y = 0)
    (ho : x-y ∈ d.kerᗮ) : projection d x = y :=
  d.ker.eq_starProjection_of_mem_orthogonal hy ho

/-- Only the kernel, rather than its presentation by a defect map, determines the projection. -/
theorem projection_eq_of_kernel_eq (e : E →L[ℝ] R) (h : d.ker = e.ker) :
    projection d = projection e := by
  ext x
  apply projection_unique d x (projection e x)
  · change projection e x ∈ d.ker
    rw [h]
    exact projection_mem e x
  · rw [h]
    exact error_orthogonal e x

/-- No smaller nonnegative constant works for all inputs with these norms. -/
theorem gain_le_of_bound (C : ℝ) (hC : 0 ≤ C)
    (hb : ∀ x, ‖x-projection d x‖ ≤ C * ‖d x‖) : gain d ≤ C := by
  apply ContinuousLinearMap.opNorm_le_bound _ hC
  intro r
  let x := (reducedEquiv d).symm r
  have hx := hb x.val
  rw [projection_orthogonal_zero d x.val x.property, sub_zero] at hx
  have hd : d x.val = r.val := by
    have he := congrArg Subtype.val ((reducedEquiv d).apply_symm_apply r)
    exact he
  simpa only [hd, Submodule.norm_coe, x, ContinuousLinearEquiv.coe_coe] using hx

theorem gain_characterization (C : ℝ) (hC : 0 ≤ C) :
    (∀ x, ‖x-projection d x‖ ≤ C * ‖d x‖) ↔ gain d ≤ C := by
  constructor
  · exact gain_le_of_bound d C hC
  · intro h x
    exact (error_bound d x).trans (mul_le_mul_of_nonneg_right h (norm_nonneg _))

/-- The degenerate all-exact case has zero gain, rather than an undefined singular value. -/
theorem gain_eq_zero_iff : gain d = 0 ↔ d = 0 := by
  constructor
  · intro hg
    ext x
    have hb := error_bound d x
    rw [hg,zero_mul] at hb
    have hx : x-projection d x=0 := norm_eq_zero.mp (le_antisymm hb (norm_nonneg _))
    have he : x=projection d x := sub_eq_zero.mp hx
    change d x=0
    rw [he]
    exact projection_exact d x
  · intro hd
    apply le_antisymm _ (gain_nonneg d)
    apply gain_le_of_bound d 0 le_rfl
    intro x
    have hx : d x=0 := by rw [hd]; rfl
    rw [projection_fixes d x hx,sub_self,norm_zero,zero_mul]

theorem stable_kernel_projection :
    ∃ C : ℝ, 0 ≤ C ∧ ∀ x, d (projection d x) = 0 ∧
      ‖x-projection d x‖ ≤ C * ‖d x‖ :=
  ⟨gain d, gain_nonneg d, fun x => ⟨projection_exact d x, error_bound d x⟩⟩

end KernelProjection
end KomorebiSpace
end
