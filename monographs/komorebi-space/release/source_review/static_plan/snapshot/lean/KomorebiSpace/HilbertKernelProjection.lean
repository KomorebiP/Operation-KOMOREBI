import Mathlib.Analysis.InnerProductSpace.Projection.Basic
import Mathlib.Analysis.Normed.Operator.Banach
import KomorebiSpace.KernelProjectionBounds
import Mathlib.Tactic.Abel
import Mathlib.Tactic.Positivity

set_option autoImplicit false

/-!
# Hilbert kernel projection: exact repair versus residual stability

The orthogonal repair exists for every bounded linear map from a real Hilbert
space. A finite residual-to-distance gain is equivalent to closed range when
the target is Banach. The inverse is constructed by the Banach open mapping
theorem, not an assumed bounded inverse. No finite dimensionality is required.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace HilbertKernelProjection
variable {E : Type u} {R : Type v}
variable [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
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

omit [CompleteSpace E] in
@[simp] theorem reduced_apply (x : d.kerᗮ) : reduced d x = d x.val := rfl

omit [CompleteSpace E] in
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

/-- Projection removes only kernel components, so the reduced range is the full range. -/
theorem reduced_range : Set.range (reduced d) = Set.range d := by
  ext y
  constructor
  · rintro ⟨x, rfl⟩
    exact ⟨x.val, rfl⟩
  · rintro ⟨x, rfl⟩
    exact ⟨⟨x - projection d x, error_orthogonal d x⟩, defect_error d x⟩

variable [CompleteSpace R]

/-- Banach's inverse theorem supplies the inverse when the actual range is closed. -/
def reducedEquiv (hd : IsClosed (Set.range d)) :
    d.kerᗮ ≃L[ℝ] LinearMap.range (reduced d).toLinearMap :=
  (reduced d).equivRange (reduced_injective d) (by rw [reduced_range]; exact hd)

variable (hd : IsClosed (Set.range d))

@[simp] theorem reducedEquiv_value (x : d.kerᗮ) :
    (reducedEquiv d hd x).val = d x.val := rfl

/-- Sharp residual-to-kernel-distance gain for the supplied norms. It is zero
when the complementary space is zero; no undefined least-positive singular
value is used in that case. -/
def gain : ℝ := ‖(reducedEquiv d hd).symm.toContinuousLinearMap‖

theorem gain_nonneg : 0 ≤ gain d hd := by
  unfold gain
  exact norm_nonneg ((reducedEquiv d hd).symm.toContinuousLinearMap)

theorem complement_bound (x : d.kerᗮ) : ‖x.val‖ ≤ gain d hd * ‖d x.val‖ := by
  have hb := (reducedEquiv d hd).symm.toContinuousLinearMap.le_opNorm (reducedEquiv d hd x)
  change ‖(reducedEquiv d hd).symm (reducedEquiv d hd x)‖ ≤ gain d hd * ‖d x.val‖ at hb
  simpa only [ContinuousLinearEquiv.symm_apply_apply, Submodule.norm_coe] using hb


/-- The formerly assumed correction estimate is derived. -/
theorem error_bound (x : E) : ‖x - projection d x‖ ≤ gain d hd * ‖d x‖ := by
  have hb := complement_bound d hd ⟨x - projection d x, error_orthogonal d x⟩
  simpa only [defect_error] using hb

omit [CompleteSpace R] in
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

omit [CompleteSpace R] in
/-- Characterization by the protected kernel and orthogonal displacement. -/
theorem projection_unique (x y : E) (hy : d y = 0)
    (ho : x-y ∈ d.kerᗮ) : projection d x = y :=
  d.ker.eq_starProjection_of_mem_orthogonal hy ho

omit [CompleteSpace R] in
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
    (hb : ∀ x, ‖x-projection d x‖ ≤ C * ‖d x‖) : gain d hd ≤ C := by
  apply ContinuousLinearMap.opNorm_le_bound _ hC
  intro r
  let x := (reducedEquiv d hd).symm r
  have hx := hb x.val
  rw [projection_orthogonal_zero d x.val x.property, sub_zero] at hx
  have hd : d x.val = r.val := by
    have he := congrArg Subtype.val ((reducedEquiv d hd).apply_symm_apply r)
    exact he
  simpa only [hd, Submodule.norm_coe, x, ContinuousLinearEquiv.coe_coe] using hx

theorem gain_characterization (C : ℝ) (hC : 0 ≤ C) :
    (∀ x, ‖x-projection d x‖ ≤ C * ‖d x‖) ↔ gain d hd ≤ C := by
  constructor
  · exact gain_le_of_bound d hd C hC
  · intro h x
    exact (error_bound d hd x).trans (mul_le_mul_of_nonneg_right h (norm_nonneg _))

/-- The degenerate all-exact case has zero gain, rather than an undefined singular value. -/
theorem gain_eq_zero_iff : gain d hd = 0 ↔ d = 0 := by
  constructor
  · intro hg
    ext x
    have hb := error_bound d hd x
    rw [hg,zero_mul] at hb
    have hx : x-projection d x=0 := norm_eq_zero.mp (le_antisymm hb (norm_nonneg _))
    have he : x=projection d x := sub_eq_zero.mp hx
    change d x=0
    rw [he]
    exact projection_exact d x
  · intro hz
    apply le_antisymm _ (gain_nonneg d hd)
    apply gain_le_of_bound d hd 0 le_rfl
    intro x
    have hx : d x=0 := by rw [hz]; rfl
    rw [projection_fixes d x hx,sub_self,norm_zero,zero_mul]

theorem stable_kernel_projection (hd : IsClosed (Set.range d)) :
    ∃ C : ℝ, 0 ≤ C ∧ ∀ x, d (projection d x) = 0 ∧
      ‖x-projection d x‖ ≤ C * ‖d x‖ :=
  ⟨gain d hd, gain_nonneg d hd, fun x => ⟨projection_exact d x, error_bound d hd x⟩⟩

omit [CompleteSpace R] in
/-- A global residual-to-distance estimate forces closed range. -/
theorem closed_range_of_bound (C : ℝ) (hC : 0 ≤ C)
    (hb : ∀ x, ‖x - projection d x‖ ≤ C * ‖d x‖) : IsClosed (Set.range d) := by
  have ha : AntilipschitzWith ⟨C, hC⟩ (reduced d) := by
    apply AntilipschitzWith.of_le_mul_dist
    intro x y
    rw [dist_eq_norm, dist_eq_norm, ← map_sub]
    change ‖(x-y).val‖ ≤ C * ‖d (x-y).val‖
    have h := hb (x-y).val
    rw [projection_orthogonal_zero d _ (x-y).property, sub_zero] at h
    exact h
  have h := ha.isClosed_range (reduced d).uniformContinuous
  rwa [reduced_range] at h

/-- The exact infinite-dimensional criterion: stability iff closed range. -/
theorem closed_range_iff_bound : IsClosed (Set.range d) ↔
    ∃ C : ℝ, 0 ≤ C ∧ ∀ x, ‖x - projection d x‖ ≤ C * ‖d x‖ := by
  constructor
  · intro h
    exact ⟨gain d h, gain_nonneg d h, error_bound d h⟩
  · rintro ⟨C, hC, hb⟩
    exact closed_range_of_bound d C hC hb

/-- No nonlinear choice of exact answers can bypass failure of the same bound. -/
theorem closed_range_iff_near_exact : IsClosed (Set.range d) ↔
    ∃ C : ℝ, 0 ≤ C ∧ ∀ x : E, ∃ y : E,
      d y = 0 ∧ ‖x-y‖ ≤ C * ‖d x‖ := by
  constructor
  · intro h
    exact ⟨gain d h, gain_nonneg d h, fun x =>
      ⟨projection d x, projection_exact d x, error_bound d h x⟩⟩
  · rintro ⟨C,hC,hb⟩
    apply closed_range_of_bound d C hC
    intro x
    obtain ⟨y,hy,he⟩ := hb x
    exact (projection_best d x y hy).trans he

/-- Unit vectors with arbitrarily small residual exclude closed range. -/
theorem not_closed_range_of_unit_witnesses
    (hw : ∀ C : ℝ, 0 ≤ C → ∃ u : E,
      u ∈ d.kerᗮ ∧ ‖u‖ = 1 ∧ C * ‖d u‖ < 1) :
    ¬ IsClosed (Set.range d) := by
  intro h
  obtain ⟨u, hu, hn, hs⟩ := hw (gain d h) (gain_nonneg d h)
  have hb := error_bound d h u
  rw [projection_orthogonal_zero d u hu, sub_zero, hn] at hb
  exact (not_lt_of_ge hb) hs

omit [CompleteSpace R] in
/-- Exact repair exists irrespective of the closed-range condition. -/
theorem unconditional_exact_repair (x : E) :
    d (projection d x) = 0 ∧ ‖projection d x‖ ≤ ‖x‖ :=
  ⟨projection_exact d x, projection_norm d x⟩

end HilbertKernelProjection
end KomorebiSpace
end
