import KomorebiSpace.HilbertKernelProjection
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

set_option autoImplicit false

/-!
# Quantitative descent through the locally exact subspace

D is the local defect, C the overlap defect. The second-stage operator is C
restricted to ker D, not the unrestricted C. The two-stage projection is proved
to equal the existing orthogonal projection for the joint defect. All constants
refer to declared norms. No stability of the restricted operator is implicit.
-/
universe u v w
noncomputable section
namespace KomorebiSpace
namespace QuantitativeDescent
open HilbertKernelProjection
variable {E : Type u} {R : Type v} {Y : Type w}
variable [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
variable [NormedAddCommGroup R] [NormedSpace ℝ R]
variable [NormedAddCommGroup Y] [NormedSpace ℝ Y]
variable (D : E →L[ℝ] R) (C : E →L[ℝ] Y)

/-- Combined local and overlap defect; its target has the product maximum norm. -/
def joint : E →L[ℝ] R × Y := D.prod C

omit [CompleteSpace E] in
@[simp] theorem joint_apply (x : E) : joint D C x = (D x, C x) := rfl

omit [CompleteSpace E] in
@[simp] theorem joint_zero_iff (x : E) : joint D C x = 0 ↔ D x = 0 ∧ C x = 0 := by
  change (D x, C x) = (0, 0) ↔ _
  simp only [Prod.mk.injEq]

/-- Overlap matching is performed inside the already locally exact space. -/
def matching : D.ker →L[ℝ] Y := C.comp D.ker.subtypeL

omit [CompleteSpace E] in
@[simp] theorem matching_apply (x : D.ker) : matching D C x = C x.val := rfl

/-- The first-stage projection retains its proof of local exactness. -/
def locallyExact : E →L[ℝ] D.ker := D.ker.orthogonalProjectionOnto

@[simp] theorem locallyExact_val (x : E) :
    (locallyExact D x).val = projection D x := rfl

/-- The second projection remains inside ker D. -/
def repair : E →L[ℝ] E :=
  D.ker.subtypeL.comp ((projection (matching D C)).comp (locallyExact D))

@[simp] theorem repair_local (x : E) : D (repair D C x) = 0 :=
  (projection (matching D C) (locallyExact D x)).property

@[simp] theorem repair_overlap (x : E) : C (repair D C x) = 0 :=
  projection_exact (matching D C) (locallyExact D x)

/-- The two-stage construction equals the canonical joint-kernel projection. -/
theorem repair_eq_projection (x : E) : repair D C x = projection (joint D C) x := by
  symm
  apply projection_unique
  · exact (joint_zero_iff D C _).mpr ⟨repair_local D C x, repair_overlap D C x⟩
  · intro y hy
    have hy' := (joint_zero_iff D C y).mp hy
    have h₁ := error_orthogonal D x y hy'.1
    have h₂ := error_orthogonal (matching D C) (locallyExact D x) ⟨y, hy'.1⟩ hy'.2
    change inner ℝ y (projection D x - repair D C x) = 0 at h₂
    change inner ℝ y (x - repair D C x) = 0
    rw [show x - repair D C x = (x - projection D x) +
      (projection D x - repair D C x) by abel, inner_add_right, h₁, h₂, add_zero]

@[simp] theorem repair_fixes (x : E) (hD : D x = 0) (hC : C x = 0) :
    repair D C x = x := by
  rw [repair_eq_projection]
  exact projection_fixes _ _ ((joint_zero_iff D C x).mpr ⟨hD, hC⟩)

@[simp] theorem repair_idempotent (x : E) : repair D C (repair D C x) = repair D C x :=
  repair_fixes D C _ (repair_local D C x) (repair_overlap D C x)

theorem repair_norm (x : E) : ‖repair D C x‖ ≤ ‖x‖ := by
  rw [repair_eq_projection]
  exact projection_norm _ _

theorem repair_best (x y : E) (hD : D y = 0) (hC : C y = 0) :
    ‖x - repair D C x‖ ≤ ‖x-y‖ := by
  rw [repair_eq_projection]
  exact projection_best _ _ _ ((joint_zero_iff D C y).mpr ⟨hD, hC⟩)

/-- Exact Pythagorean distance to any other globally coherent candidate. -/
theorem distance_squared (x y : E) (hD : D y=0) (hC : C y=0) :
    ‖x-y‖^2=‖x-repair D C x‖^2+‖repair D C x-y‖^2 := by
  have he : inner ℝ (x-repair D C x) (repair D C x-y)=0 := by
    rw [real_inner_comm, repair_eq_projection]
    apply error_orthogonal (joint D C) x
    change joint D C (projection (joint D C) x-y)=0
    rw [map_sub, projection_exact, (joint_zero_iff D C y).mpr ⟨hD,hC⟩,sub_self]
  rw [show x-y=(x-repair D C x)+(repair D C x-y) by abel,
    norm_add_sq_real,he,mul_zero,add_zero]

/-- The constructed global repair is the unique nearest joint-exact candidate. -/
theorem nearest_unique (x y : E) (hD : D y=0) (hC : C y=0)
    (hnear : ‖x-y‖ ≤ ‖x-repair D C x‖) : y=repair D C x := by
  have he := distance_squared D C x y hD hC
  have hsq : ‖repair D C x-y‖^2=0 := by
    nlinarith [norm_nonneg (x-y),norm_nonneg (x-repair D C x),
      sq_nonneg ‖repair D C x-y‖]
  have hn : ‖repair D C x-y‖=0 := by nlinarith [norm_nonneg (repair D C x-y)]
  exact (sub_eq_zero.mp (norm_eq_zero.mp hn)).symm

/-- Exact orthogonality of local error and the subsequent matching correction. -/
theorem errors_orthogonal (x : E) :
    inner ℝ (x - projection D x) (projection D x - repair D C x) = 0 := by
  rw [real_inner_comm]
  apply error_orthogonal D x
  change D (projection D x - repair D C x) = 0
  rw [map_sub, projection_exact, repair_local, sub_self]

/-- Pythagoras separates local correction from restricted overlap correction. -/
theorem error_squared (x : E) :
    ‖x-repair D C x‖^2 = ‖x-projection D x‖^2 +
      ‖projection D x-repair D C x‖^2 := by
  rw [show x-repair D C x = (x-projection D x) +
    (projection D x-repair D C x) by abel]
  rw [norm_add_sq_real, errors_orthogonal, mul_zero, add_zero]

/-- A norm bound on C only in directions removed by the first projection. -/
def InteractionBound (γ : ℝ) : Prop :=
  ∀ u : E, u ∈ D.kerᗮ → ‖C u‖ ≤ γ * ‖u‖

omit [CompleteSpace E] in
theorem operator_interaction : InteractionBound D C ‖C‖ := by
  intro u _
  exact C.le_opNorm u

theorem matching_input_bound {a γ : ℝ}
    (hlocal : ∀ x, ‖x-projection D x‖ ≤ a*‖D x‖)
    (hγ : 0 ≤ γ) (hint : InteractionBound D C γ) (x : E) :
    ‖matching D C (locallyExact D x)‖ ≤ ‖C x‖ + γ*a*‖D x‖ := by
  change ‖C (projection D x)‖ ≤ _
  calc
    _ = ‖C x - C (x-projection D x)‖ := by rw [map_sub]; congr 1; abel
    _ ≤ ‖C x‖ + ‖C (x-projection D x)‖ := norm_sub_le _ _
    _ ≤ ‖C x‖ + γ*‖x-projection D x‖ :=
      add_le_add le_rfl (hint _ (error_orthogonal D x))
    _ ≤ _ := by
      have h := mul_le_mul_of_nonneg_left (hlocal x) hγ
      nlinarith

/-- Two distinct measured defects control the actual global correction. -/
theorem repair_error {a b γ : ℝ} (hb : 0 ≤ b) (hγ : 0 ≤ γ)
    (hlocal : ∀ x, ‖x-projection D x‖ ≤ a*‖D x‖)
    (hmatch : ∀ z, ‖z-projection (matching D C) z‖ ≤ b*‖matching D C z‖)
    (hint : InteractionBound D C γ) (x : E) :
    ‖x-repair D C x‖ ≤ a*(1+b*γ)*‖D x‖ + b*‖C x‖ := by
  have h₂ := hmatch (locallyExact D x)
  change ‖projection D x-repair D C x‖ ≤ b*‖matching D C (locallyExact D x)‖ at h₂
  have h₃ := mul_le_mul_of_nonneg_left
    (matching_input_bound D C hlocal hγ hint x) hb
  have ht := norm_sub_le_norm_sub_add_norm_sub x (projection D x) (repair D C x)
  nlinarith [hlocal x]

/-- Sharper squared bound from the orthogonal two-stage decomposition. -/
theorem repair_error_squared {a b γ : ℝ} (ha : 0 ≤ a) (hb : 0 ≤ b) (hγ : 0 ≤ γ)
    (hlocal : ∀ x, ‖x-projection D x‖ ≤ a*‖D x‖)
    (hmatch : ∀ z, ‖z-projection (matching D C) z‖ ≤ b*‖matching D C z‖)
    (hint : InteractionBound D C γ) (x : E) :
    ‖x-repair D C x‖^2 ≤ (a*‖D x‖)^2 +
      (b*(‖C x‖+γ*a*‖D x‖))^2 := by
  have h₁ := hlocal x
  have h₂ := (hmatch (locallyExact D x)).trans
    (mul_le_mul_of_nonneg_left (matching_input_bound D C hlocal hγ hint x) hb)
  change ‖projection D x-repair D C x‖ ≤ b*(‖C x‖+γ*a*‖D x‖) at h₂
  rw [error_squared]
  have hn₁ := norm_nonneg (x-projection D x)
  have hn₂ := norm_nonneg (projection D x-repair D C x)
  have hn₃ : 0 ≤ a*‖D x‖ := mul_nonneg ha (norm_nonneg _)
  nlinarith [sq_nonneg (a*‖D x‖-‖x-projection D x‖),
    sq_nonneg (b*(‖C x‖+γ*a*‖D x‖)-‖projection D x-repair D C x‖)]

end QuantitativeDescent
end KomorebiSpace
end
