import KomorebiSpace.QuantitativeDescent

set_option autoImplicit false
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

@[simp] theorem locallyExact_coe (z : D.ker) : locallyExact D z.val = z := by
  apply Subtype.ext
  exact projection_fixes D z.val z.property

@[simp] theorem repair_of_local (z : D.ker) :
    repair D C z.val = (projection (matching D C) z).val := by
  change (projection (matching D C) (locallyExact D z.val)).val = _
  rw [locallyExact_coe]

/-- Uncertain measurements are allowances, not equality with exact residuals. -/
theorem measured_error {a b γ : ℝ} (ha : 0 ≤ a) (hb : 0 ≤ b) (hγ : 0 ≤ γ)
    (hlocal : ∀ x, ‖x-projection D x‖ ≤ a*‖D x‖)
    (hmatch : ∀ z, ‖z-projection (matching D C) z‖ ≤ b*‖matching D C z‖)
    (hint : InteractionBound D C γ) (x : E) (r : R) (s : Y)
    {η₁ η₂ : ℝ} (h₁ : ‖D x-r‖ ≤ η₁) (h₂ : ‖C x-s‖ ≤ η₂) :
    ‖x-repair D C x‖ ≤ a*(1+b*γ)*(‖r‖+η₁)+b*(‖s‖+η₂) := by
  have hD : ‖D x‖ ≤ ‖r‖+η₁ := by
    have h := norm_sub_le_norm_sub_add_norm_sub (D x) r 0
    simp only [sub_zero] at h
    linarith
  have hC : ‖C x‖ ≤ ‖s‖+η₂ := by
    have h := norm_sub_le_norm_sub_add_norm_sub (C x) s 0
    simp only [sub_zero] at h
    linarith
  have hn : 0 ≤ a*(1+b*γ) := by positivity
  exact (repair_error D C hb hγ hlocal hmatch hint x).trans
    (add_le_add (mul_le_mul_of_nonneg_left hD hn) (mul_le_mul_of_nonneg_left hC hb))

variable [CompleteSpace R] [CompleteSpace Y]

/-- Closed joint range forces stability of overlap matching within locally exact data. -/
theorem matching_closed_of_joint_closed
    (h : IsClosed (Set.range (joint D C))) : IsClosed (Set.range (matching D C)) := by
  obtain ⟨b, hb, he⟩ := (closed_range_iff_bound (joint D C)).mp h
  apply closed_range_of_bound (matching D C) b hb
  intro z
  have hz := he z.val
  rw [← repair_eq_projection, repair_of_local] at hz
  change ‖z.val - (projection (matching D C) z).val‖ ≤ b*‖(D z.val,C z.val)‖ at hz
  have hzD : D z.val = 0 := z.property
  rw [hzD, Prod.norm_def, norm_zero, max_eq_right (norm_nonneg _)] at hz
  exact hz

/-- The sufficient global coefficient is derived from the two actual closed ranges. -/
def stabilityGain (hD : IsClosed (Set.range D))
    (hB : IsClosed (Set.range (matching D C))) : ℝ :=
  gain D hD * (1 + gain (matching D C) hB * ‖C‖) + gain (matching D C) hB

theorem stabilityGain_nonneg (hD : IsClosed (Set.range D))
    (hB : IsClosed (Set.range (matching D C))) : 0 ≤ stabilityGain D C hD hB := by
  have ha := gain_nonneg D hD
  have hb := gain_nonneg (matching D C) hB
  unfold stabilityGain
  positivity

theorem stable_repair (hD : IsClosed (Set.range D))
    (hB : IsClosed (Set.range (matching D C))) (x : E) :
    ‖x-repair D C x‖ ≤ stabilityGain D C hD hB * ‖joint D C x‖ := by
  have he := repair_error D C (gain_nonneg _ hB) (norm_nonneg C)
    (error_bound D hD) (error_bound _ hB) (operator_interaction D C) x
  have h₁ := le_max_left ‖D x‖ ‖C x‖
  have h₂ := le_max_right ‖D x‖ ‖C x‖
  have ha := gain_nonneg D hD
  have hb := gain_nonneg (matching D C) hB
  have hn : 0 ≤ gain D hD * (1 + gain (matching D C) hB * ‖C‖) := by positivity
  have ht := add_le_add (mul_le_mul_of_nonneg_left h₁ hn)
    (mul_le_mul_of_nonneg_left h₂ (gain_nonneg _ hB))
  change _ ≤ stabilityGain D C hD hB * max ‖D x‖ ‖C x‖
  exact he.trans (by simpa only [stabilityGain, add_mul] using ht)

theorem joint_closed_of_matching_closed (hD : IsClosed (Set.range D))
    (hB : IsClosed (Set.range (matching D C))) : IsClosed (Set.range (joint D C)) := by
  apply closed_range_of_bound _ (stabilityGain D C hD hB) (stabilityGain_nonneg D C hD hB)
  intro x
  rw [← repair_eq_projection]
  exact stable_repair D C hD hB x

/-- Local stability isolates the precise remaining global stability obligation. -/
theorem joint_closed_iff_matching_closed (hD : IsClosed (Set.range D)) :
    IsClosed (Set.range (joint D C)) ↔ IsClosed (Set.range (matching D C)) :=
  ⟨matching_closed_of_joint_closed D C, joint_closed_of_matching_closed D C hD⟩

/-- Even an arbitrary nonlinear selection of global exact outputs cannot evade this criterion. -/
theorem matching_closed_iff_near_joint (hD : IsClosed (Set.range D)) :
    IsClosed (Set.range (matching D C)) ↔
      ∃ M : ℝ, 0 ≤ M ∧ ∀ x : E, ∃ y : E,
        D y = 0 ∧ C y = 0 ∧ ‖x-y‖ ≤ M*‖joint D C x‖ := by
  rw [← joint_closed_iff_matching_closed D C hD, closed_range_iff_near_exact]
  simp only [joint_zero_iff, and_assoc]

end QuantitativeDescent
end KomorebiSpace
end
