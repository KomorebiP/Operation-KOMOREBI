import KomorebiSpace.HilbertKernelProjection
import Mathlib.Tactic.Linarith

set_option autoImplicit false

/-!
# Robust residual certificates

Measurement error, operator error, and change of the exact kernel are separated.
A common-kernel conclusion is derived from preservation of the old kernel and a
strict perturbation budget. Without preservation, the bound is to the old exact
space and includes an input-size term. No noisy value is reclassified as exact.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace ResidualRobustness
open HilbertKernelProjection
variable {E : Type u} {R : Type v}
variable [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
variable [NormedAddCommGroup R] [NormedSpace ℝ R]

/-- Evidence about the actual canonical projection, not a numerical success flag. -/
structure Bound (d : E →L[ℝ] R) where
  constant : ℝ
  nonneg : 0 ≤ constant
  estimate : ∀ x, ‖x-projection d x‖ ≤ constant*‖d x‖

namespace Bound
variable {d : E →L[ℝ] R} (B : Bound d)

/-- A certified residual ball bounds the distance to the original exact space. -/
theorem measured (x : E) (y : R) (η : ℝ) (hy : ‖d x-y‖≤η) :
    ‖x-projection d x‖≤B.constant*(‖y‖+η) := by
  apply (B.estimate x).trans
  apply mul_le_mul_of_nonneg_left _ B.nonneg
  calc
    ‖d x‖ ≤ ‖d x-y‖+‖y‖ := by
      simpa only [sub_add_cancel] using norm_add_le (d x-y) y
    _ ≤ ‖y‖+η := by linarith

/-- With no kernel-preservation assumption, operator error costs epsilon times
input size. The conclusion still concerns the reference exact space. -/
theorem uncertain_operator (e : E →L[ℝ] R) (ε η : ℝ)
    (he : ∀ x, ‖(d-e) x‖≤ε*‖x‖) (x : E) (y : R) (hy : ‖e x-y‖≤η) :
    ‖x-projection d x‖≤B.constant*(‖y‖+η+ε*‖x‖) := by
  apply (B.estimate x).trans
  apply mul_le_mul_of_nonneg_left _ B.nonneg
  have ht : ‖d x‖≤‖(d-e) x‖+‖e x-y‖+‖y‖ := by
    have h := norm_add_le ((d-e) x) (e x-y)
    have h' := norm_add_le ((d-e) x+(e x-y)) y
    have hid : (d-e) x+(e x-y)+y=d x := by simp only [sub_apply]; abel
    rw [hid] at h'
    linarith
  have hp := he x
  linarith

/-- Operator-norm uncertainty implies the pointwise estimate used above. -/
theorem uncertain_operator_opNorm (e : E →L[ℝ] R) (ε η : ℝ)
    (he : ‖d-e‖≤ε) (x : E) (y : R) (hy : ‖e x-y‖≤η) :
    ‖x-projection d x‖≤B.constant*(‖y‖+η+ε*‖x‖) :=
  B.uncertain_operator e ε η (fun z => ((d-e).le_opNorm z).trans
    (mul_le_mul_of_nonneg_right he (norm_nonneg z))) x y hy

/-- The direction of exact-space comparison that needs no preservation premise. -/
theorem new_exact_near_old (e : E →L[ℝ] R) (ε : ℝ)
    (he : ∀ x, ‖(d-e) x‖≤ε*‖x‖) (x : E) (hx : e x=0) :
    ‖x-projection d x‖≤B.constant*ε*‖x‖ := by
  have h := B.uncertain_operator e ε 0 he x 0 (by simp [hx])
  simpa only [norm_zero,add_zero,zero_add,mul_assoc] using h

/-- A preserved exact component plus a strict radius excludes new null modes. -/
theorem preserved_kernel_bound (e : E →L[ℝ] R) (ε : ℝ)
    (he : ∀ x, ‖(d-e) x‖≤ε*‖x‖)
    (hpres : ∀ x, e (projection d x)=0) (hradius : B.constant*ε<1) (x : E) :
    ‖x-projection d x‖≤(B.constant/(1-B.constant*ε))*‖e x‖ := by
  let u := x-projection d x
  have hdu : d u=d x := defect_error d x
  have heu : e u=e x := by simp only [u,map_sub,hpres,sub_zero]
  have htri : ‖d x‖≤‖e x‖+ε*‖u‖ := by
    calc
      ‖d x‖ = ‖(d-e) u+e u‖ := by simp only [sub_apply,sub_add_cancel,hdu]
      _ ≤ ‖(d-e) u‖+‖e u‖ := norm_add_le _ _
      _ ≤ ‖e x‖+ε*‖u‖ := by rw [heu]; linarith [he u]
  have hb := (B.estimate x).trans (mul_le_mul_of_nonneg_left htri B.nonneg)
  have hp : 0<1-B.constant*ε := sub_pos.mpr hradius
  have hh : (1-B.constant*ε)*‖x-projection d x‖≤B.constant*‖e x‖ := by
    dsimp only [u] at hb
    nlinarith
  calc
    _ ≤ (B.constant*‖e x‖)/(1-B.constant*ε) :=
      (le_div_iff₀ hp).mpr (by nlinarith [hh])
    _ = _ := by ring

/-- Equality of kernels is a conclusion, not an input field. -/
theorem kernels_equal (e : E →L[ℝ] R) (ε : ℝ)
    (he : ∀ x, ‖(d-e) x‖≤ε*‖x‖)
    (hpres : ∀ x, e (projection d x)=0) (hradius : B.constant*ε<1) : d.ker=e.ker := by
  ext x
  change d x=0 ↔ e x=0
  constructor
  · intro hx
    simpa only [projection_fixes d x hx] using hpres x
  · intro hx
    have hb := B.preserved_kernel_bound e ε he hpres hradius x
    rw [hx,norm_zero,mul_zero] at hb
    have hz : x=projection d x := sub_eq_zero.mp (norm_eq_zero.mp
      (le_antisymm hb (norm_nonneg _)))
    rw [hz]
    exact projection_exact d x

/-- The same canonical exact repair works for every admitted perturbation. -/
theorem projections_equal (e : E →L[ℝ] R) (ε : ℝ)
    (he : ∀ x, ‖(d-e) x‖≤ε*‖x‖)
    (hpres : ∀ x, e (projection d x)=0) (hradius : B.constant*ε<1) :
    projection d=projection e :=
  projection_eq_of_kernel_eq d e (B.kernels_equal e ε he hpres hradius)

/-- A robustness certificate with an explicitly degraded gain. -/
def perturb (e : E →L[ℝ] R) (ε : ℝ)
    (he : ∀ x, ‖(d-e) x‖≤ε*‖x‖)
    (hpres : ∀ x, e (projection d x)=0) (hradius : B.constant*ε<1) : Bound e where
  constant := B.constant/(1-B.constant*ε)
  nonneg := div_nonneg B.nonneg (le_of_lt (sub_pos.mpr hradius))
  estimate x := by
    rw [← B.projections_equal e ε he hpres hradius]
    exact B.preserved_kernel_bound e ε he hpres hradius x

/-- The perturbed range is closed under the same explicit assumptions. -/
theorem perturbed_closed_range (e : E →L[ℝ] R) (ε : ℝ)
    (he : ∀ x, ‖(d-e) x‖≤ε*‖x‖)
    (hpres : ∀ x, e (projection d x)=0) (hradius : B.constant*ε<1) :
    IsClosed (Set.range e) :=
  closed_range_of_bound e (B.perturb e ε he hpres hradius).constant
    (B.perturb e ε he hpres hradius).nonneg
    (B.perturb e ε he hpres hradius).estimate

/-- Measurement uncertainty for a kernel-preserving operator perturbation. -/
theorem perturbed_measured (e : E →L[ℝ] R) (ε η : ℝ)
    (he : ∀ x, ‖(d-e) x‖≤ε*‖x‖)
    (hpres : ∀ x, e (projection d x)=0) (hradius : B.constant*ε<1)
    (x : E) (y : R) (hy : ‖e x-y‖≤η) :
    ‖x-projection d x‖≤(B.constant/(1-B.constant*ε))*(‖y‖+η) := by
  have h := (B.perturb e ε he hpres hradius).measured x y η hy
  simpa only [perturb,← B.projections_equal e ε he hpres hradius] using h

end Bound
end ResidualRobustness
end KomorebiSpace
end
