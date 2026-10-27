import Mathlib.Analysis.Normed.Operator.NormedSpace
import Mathlib.Tactic.Abel
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

set_option autoImplicit false

/-!
# Intrinsic exact core and changes of residual coordinates

The kernel and residual space are fixed by the differential. A bounded right
inverse selects a chart and a retraction, not a new exact core. Differences
between right inverses take values in that core. No completeness is needed.
-/
universe u v w
noncomputable section
namespace KomorebiSpace
namespace SplitDefect
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable {E : Type v} [NormedAddCommGroup E] [NormedSpace 𝕜 E]
variable {R : Type w} [NormedAddCommGroup R] [NormedSpace 𝕜 R]
variable (d : E →L[𝕜] R)

/-- A chosen bounded right inverse of the fixed differential. -/
structure Section where
  lift : R →L[𝕜] E
  right_inv : ∀ r, d (lift r) = r

/-- This space is independent of any section. -/
abbrev Core := d.ker

namespace Section
variable {d} (A B C : Section d)

@[ext] theorem ext (h : A.lift = B.lift) : A = B := by
  cases A
  cases B
  cases h
  rfl

/-- The retraction onto the fixed exact core selected by the section. -/
def project : E →L[𝕜] E :=
  ContinuousLinearMap.id 𝕜 E - A.lift.comp d

@[simp] theorem project_apply (f : E) : A.project f = f - A.lift (d f) := rfl

@[simp] theorem project_exact (f : E) : d (A.project f) = 0 := by
  simp only [project_apply, map_sub, A.right_inv, sub_self]

@[simp] theorem project_fixes (f : E) (hf : d f = 0) : A.project f = f := by
  simp [project_apply, hf]

@[simp] theorem project_idempotent (f : E) : A.project (A.project f) = A.project f :=
  A.project_fixes _ (A.project_exact f)

@[simp] theorem project_lift (r : R) : A.project (A.lift r) = 0 := by
  simp only [project_apply, A.right_inv, sub_self]

/-- The displacement from chart B to chart A, with values in the exact core. -/
def difference : R →L[𝕜] Core d :=
  (A.lift - B.lift).codRestrict (Core d) (fun r => by
    change d (A.lift r - B.lift r) = 0
    rw [map_sub, A.right_inv, B.right_inv, sub_self])

@[simp] theorem difference_apply (r : R) :
    (A.difference B r : E) = A.lift r - B.lift r := rfl

@[simp] theorem difference_exact (r : R) : d (A.lift r - B.lift r) = 0 := by
  rw [map_sub, A.right_inv, B.right_inv, sub_self]

@[simp] theorem difference_self : A.difference A = 0 := by
  ext r
  simp

theorem difference_add (r : R) :
    A.difference C r = A.difference B r + B.difference C r := by
  apply Subtype.ext
  change A.lift r - C.lift r = (A.lift r - B.lift r) + (B.lift r - C.lift r)
  abel

theorem project_change (f : E) :
    B.project f - A.project f = (A.difference B (d f) : E) := by
  simp only [project_apply, difference_apply]
  abel

theorem project_change_norm (f : E) :
    ‖B.project f - A.project f‖ ≤ ‖A.lift - B.lift‖ * ‖d f‖ := by
  rw [project_change, difference_apply]
  exact (A.lift - B.lift).le_opNorm (d f)

/-- Both retractions act as the identity on the same exact core. -/
@[simp] theorem project_other (f : E) : A.project (B.project f) = B.project f :=
  A.project_fixes _ (B.project_exact f)

/-- Retractions onto the same core need not commute. -/
theorem projects_commute_iff :
    A.project.comp B.project = B.project.comp A.project ↔ A.project = B.project := by
  constructor
  · intro h
    ext f
    have hx := congrArg (fun T : E →L[𝕜] E => T f) h
    simpa only [ContinuousLinearMap.comp_apply, project_other] using hx.symm
  · intro h
    rw [h]

/-- Surjectivity of the differential makes the chosen section recoverable from its retraction. -/
theorem projects_equal_iff_lifts_equal : A.project = B.project ↔ A.lift = B.lift := by
  constructor
  · intro h
    ext r
    have h0 : B.project (A.lift r) = 0 := by
      rw [← h]
      exact A.project_lift r
    have hx : A.lift r - B.lift r = 0 := by
      simpa only [project_apply, A.right_inv] using h0
    exact sub_eq_zero.mp hx
  · intro h
    unfold project
    rw [h]

/-- Explicit linear coordinates: exact component and unchanged residual. -/
def chartLinear : E ≃ₗ[𝕜] (Core d × R) where
  toFun f := (⟨A.project f, A.project_exact f⟩, d f)
  invFun z := z.1.val + A.lift z.2
  left_inv f := by
    change f - A.lift (d f) + A.lift (d f) = f
    abel
  right_inv z := by
    apply Prod.ext
    · apply Subtype.ext
      change A.project (z.1.val + A.lift z.2) = z.1.val
      rw [map_add, project_lift, add_zero]
      exact A.project_fixes _ z.1.property
    · change d (z.1.val + A.lift z.2) = z.2
      have hz : d z.1.val = 0 := z.1.property
      rw [map_add, hz, A.right_inv, zero_add]
  map_add' f g := by
    apply Prod.ext
    · apply Subtype.ext
      exact map_add A.project f g
    · exact map_add d f g
  map_smul' c f := by
    apply Prod.ext
    · apply Subtype.ext
      exact map_smul A.project c f
    · exact map_smul d c f

theorem chart_bound (f : E) :
    ‖A.chartLinear f‖ ≤ max ‖A.project‖ ‖d‖ * ‖f‖ := by
  change max ‖A.project f‖ ‖d f‖ ≤ _
  apply max_le
  · exact (A.project.le_opNorm f).trans
      (mul_le_mul_of_nonneg_right (le_max_left _ _) (norm_nonneg f))
  · exact (d.le_opNorm f).trans
      (mul_le_mul_of_nonneg_right (le_max_right _ _) (norm_nonneg f))

theorem chart_inverse_bound (z : Core d × R) :
    ‖A.chartLinear.symm z‖ ≤ (1 + ‖A.lift‖) * ‖z‖ := by
  have h1 : ‖z.1.val‖ ≤ ‖z‖ := le_max_left _ _
  have h2 : ‖z.2‖ ≤ ‖z‖ := le_max_right _ _
  calc
    ‖A.chartLinear.symm z‖ ≤ ‖z.1.val‖ + ‖A.lift z.2‖ := norm_add_le _ _
    _ ≤ ‖z‖ + ‖A.lift‖ * ‖z.2‖ := add_le_add h1 (A.lift.le_opNorm _)
    _ ≤ ‖z‖ + ‖A.lift‖ * ‖z‖ :=
      add_le_add le_rfl (mul_le_mul_of_nonneg_left h2 (norm_nonneg _))
    _ = (1 + ‖A.lift‖) * ‖z‖ := by ring

/-- A bounded linear isomorphism, not an isometry. -/
def chart : E ≃L[𝕜] (Core d × R) :=
  A.chartLinear.toContinuousLinearEquivOfBounds
    (max ‖A.project‖ ‖d‖) (1 + ‖A.lift‖) A.chart_bound A.chart_inverse_bound

@[simp] theorem chart_exact_component (f : E) : (A.chart f).1.val = A.project f := rfl
@[simp] theorem chart_residual (f : E) : (A.chart f).2 = d f := rfl
@[simp] theorem chart_inverse (z : Core d × R) : A.chart.symm z = z.1.val + A.lift z.2 := rfl

/-- The transition acts on the same product, since neither factor depends on A. -/
def transition : (Core d × R) ≃L[𝕜] (Core d × R) := A.chart.symm.trans B.chart

/-- All chart changes are triangular shears, fixing the residual coordinate. -/
theorem transition_formula (z : Core d × R) :
    A.transition B z = (z.1 + A.difference B z.2, z.2) := by
  apply Prod.ext
  · apply Subtype.ext
    change B.project (z.1.val + A.lift z.2) = z.1.val + (A.lift z.2 - B.lift z.2)
    have hz : d z.1.val = 0 := z.1.property
    rw [project_apply, map_add, hz, A.right_inv, zero_add]
    abel
  · change d (z.1.val + A.lift z.2) = z.2
    have hz : d z.1.val = 0 := z.1.property
    rw [map_add, hz, A.right_inv, zero_add]

@[simp] theorem transition_residual (z : Core d × R) : (A.transition B z).2 = z.2 := by
  rw [transition_formula]

@[simp] theorem transition_exact_slice (e : Core d) : A.transition B (e, 0) = (e, 0) := by
  rw [transition_formula]
  simp

@[simp] theorem transition_self (z : Core d × R) : A.transition A z = z := by
  rw [transition_formula]
  simp

/-- The cocycle law is proved for the actual coordinate transitions. -/
theorem transition_cocycle (z : Core d × R) :
    B.transition C (A.transition B z) = A.transition C z := by
  rw [transition_formula, transition_formula, transition_formula, A.difference_add B C]
  simp only [Prod.mk.injEq, and_true]
  abel

theorem transition_norm (z : Core d × R) :
    ‖A.transition B z‖ ≤ (1 + ‖A.lift - B.lift‖) * ‖z‖ := by
  rw [transition_formula]
  change max ‖z.1.val + (A.lift z.2 - B.lift z.2)‖ ‖z.2‖ ≤ _
  have h1 : ‖z.1.val‖ ≤ ‖z‖ := le_max_left _ _
  have h2 : ‖z.2‖ ≤ ‖z‖ := le_max_right _ _
  have h3 : ‖A.lift z.2 - B.lift z.2‖ ≤ ‖A.lift - B.lift‖ * ‖z‖ :=
    ((A.lift - B.lift).le_opNorm _).trans
      (mul_le_mul_of_nonneg_left h2 (norm_nonneg _))
  apply max_le
  · calc
      _ ≤ ‖z.1.val‖ + ‖A.lift z.2 - B.lift z.2‖ := norm_add_le _ _
      _ ≤ ‖z‖ + ‖A.lift - B.lift‖ * ‖z‖ := add_le_add h1 h3
      _ = _ := by ring
  · have hnon := mul_nonneg (norm_nonneg (A.lift - B.lift)) (norm_nonneg z)
    nlinarith

/-- Add any exact-valued bounded map to a section; it remains a section. -/
def translate (T : R →L[𝕜] Core d) : Section d where
  lift := A.lift + (Core d).subtypeL.comp T
  right_inv r := by
    change d (A.lift r + (T r : E)) = r
    have ht : d (T r : E) = 0 := (T r).property
    rw [map_add, A.right_inv, ht, add_zero]

@[simp] theorem translate_apply (T : R →L[𝕜] Core d) (r : R) :
    (A.translate T).lift r = A.lift r + (T r : E) := rfl

/-- Every other section differs by a unique exact-valued map. -/
def sectionParameters : (R →L[𝕜] Core d) ≃ Section d where
  toFun := A.translate
  invFun B := B.difference A
  left_inv T := by
    ext r
    simp only [difference_apply, translate_apply]
    abel
  right_inv B := by
    apply Section.ext
    ext r
    change A.lift r + (B.lift r - A.lift r) = B.lift r
    abel

end Section
end SplitDefect
end KomorebiSpace
end
