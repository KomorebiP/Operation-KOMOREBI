import PaperXI.HeisenbergGroup
import PaperXI.HeisenbergCardinality
import Mathlib.GroupTheory.Subgroup.Center
import Mathlib.Tactic.LinearCombination

/-! The center is proved to consist exactly of the central-coordinate elements. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergCenter

open PaperXI.Heisenberg PaperXI.HeisenbergForm

variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X]

theorem commute_iff (h2 : (2 : K) ≠ 0) (a b : Element K X) :
    a * b = b * a ↔ form (a.position, a.frequency) (b.position, b.frequency) = 0 := by
  constructor
  · intro h
    have hc := congrArg Element.central h
    simp only [mul_central] at hc
    have hz : 2 * (2 : K)⁻¹ *
        (b.frequency a.position - a.frequency b.position) = 0 := by
      linear_combination hc
    simpa [h2] using hz
  · intro h
    have hz : b.frequency a.position - a.frequency b.position = 0 := h
    have hr : a.frequency b.position - b.frequency a.position = 0 := by
      rw [sub_eq_zero] at hz ⊢
      exact hz.symm
    apply Element.ext
    · exact add_comm _ _
    · exact add_comm _ _
    · simp [mul_central, hz, hr, add_comm]

theorem mem_center_iff (h2 : (2 : K) ≠ 0) (a : Element K X) :
    a ∈ Subgroup.center (Element K X) ↔ a.position = 0 ∧ a.frequency = 0 := by
  constructor
  · intro h
    have hz : (a.position, a.frequency) = 0 :=
      (HeisenbergCardinality.form_forall_eq_zero_iff _).mp (by
        intro w
        exact (commute_iff h2 a ⟨w.1, w.2, 0⟩).mp
          ((Subgroup.mem_center_iff.mp h _).symm))
    exact ⟨congrArg Prod.fst hz, congrArg Prod.snd hz⟩
  · rintro ⟨hx, hξ⟩
    apply Subgroup.mem_center_iff.mpr
    intro b
    apply (commute_iff h2 b a).mpr
    simp [hx, hξ]

theorem center_eq_centralElement (h2 : (2 : K) ≠ 0) (a : Element K X) :
    a ∈ Subgroup.center (Element K X) ↔ a = centralElement a.central := by
  rw [mem_center_iff h2]
  constructor
  · rintro ⟨hx, hξ⟩
    apply Element.ext
    · exact hx
    · exact hξ
    · rfl
  · intro h
    exact ⟨by simpa using congrArg Element.position h,
      by simpa using congrArg Element.frequency h⟩

end PaperXI.HeisenbergCenter
