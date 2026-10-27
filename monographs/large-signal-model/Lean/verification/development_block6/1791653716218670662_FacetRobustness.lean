import KomorebiLSM.RobustFiniteDomains
import Mathlib.Analysis.Normed.Operator.Basic

/-! P40 norm-ball certificate. Facets must describe the whole generated cone;
normalization is an additional exact condition, not a consequence of the margin. -/
set_option autoImplicit false
namespace Komorebi.LSM.RobustDomains
open PositiveLift
variable {E I J : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- Coefficient perturbation is controlled in the declared operator/dual norms. -/
theorem facet_error_bound (g : E →L[ℝ] ℝ) (B D : E →L[ℝ] E)
    (ε : ℝ) (hε : ‖B-D‖ ≤ ε) (v : E) :
    |g (B v)-g (D v)| ≤ ε * ‖g‖ * ‖v‖ := by
  have he : g (B v)-g (D v) = g ((B-D) v) := by simp only [map_sub,sub_apply]
  rw [he,← Real.norm_eq_abs]
  calc
    ‖g ((B-D) v)‖ ≤ ‖g‖ * ‖(B-D) v‖ := g.le_opNorm _
    _ ≤ ‖g‖ * (‖B-D‖ * ‖v‖) :=
      mul_le_mul_of_nonneg_left ((B-D).le_opNorm v) (norm_nonneg _)
    _ ≤ ‖g‖ * (ε * ‖v‖) := mul_le_mul_of_nonneg_left
      (mul_le_mul_of_nonneg_right hε (norm_nonneg _)) (norm_nonneg _)
    _ = ε * ‖g‖ * ‖v‖ := by ring

/-- Every perturbed generator image lies on the positive side of every facet. -/
theorem facet_margin_robust (g : E →L[ℝ] ℝ) (B D : E →L[ℝ] E)
    (ε : ℝ) (hε : ‖B-D‖ ≤ ε) (v : E)
    (hm : ε * ‖g‖ * ‖v‖ ≤ g (D v)) : 0 ≤ g (B v) := by
  have he := (abs_le.mp (facet_error_bound g B D ε hε v)).1
  linarith

theorem facet_norm_ball_invariant [Fintype J] [DecidableEq J]
    (V : (J → ℝ) →ₗ[ℝ] E) (g : I → E →L[ℝ] ℝ)
    (hfacets : hull V = {x | ∀ i, 0 ≤ g i x})
    (B D : E →L[ℝ] E) (ε : ℝ) (hε : ‖B-D‖ ≤ ε)
    (hm : ∀ i j, ε * ‖g i‖ * ‖generator V j‖ ≤ g i (D (generator V j))) :
    ∀ x ∈ hull V, B x ∈ hull V := by
  apply (invariant_iff_generators V B.toLinearMap).mpr
  intro j
  rw [hfacets]
  exact fun i => facet_margin_robust (g i) B D ε hε _ (hm i j)

/-- The robust facet statement also constructs a nonnegative perturbed lift. -/
theorem facet_norm_ball_lift [Fintype J] [DecidableEq J]
    (V : (J → ℝ) →ₗ[ℝ] E) (g : I → E →L[ℝ] ℝ)
    (hfacets : hull V = {x | ∀ i, 0 ≤ g i x})
    (B D : E →L[ℝ] E) (ε : ℝ) (hε : ‖B-D‖ ≤ ε)
    (hm : ∀ i j, ε * ‖g i‖ * ‖generator V j‖ ≤ g i (D (generator V j))) :
    ∃ M : Matrix J J ℝ, (∀ i j, 0 ≤ M i j) ∧ B.toLinearMap.comp V = V.comp M.mulVecLin :=
  (positive_lift_iff V B.toLinearMap).mp (facet_norm_ball_invariant V g hfacets B D ε hε hm)

end Komorebi.LSM.RobustDomains
