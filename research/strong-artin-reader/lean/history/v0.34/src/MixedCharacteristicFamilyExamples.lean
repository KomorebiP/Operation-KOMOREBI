import MixedCharacteristicNormExamples

/-! Literal mixed-characteristic prescriptions. Their inherited matching class
remains nonzero when individually liftable powers cannot share a Frobenius. -/
noncomputable section
namespace Komorebi.StrongArtin.MixedCharacteristic.Examples

def familyDegree (i : Bool) : ℕ := if i then 3 else 1

def incompatibleTarget (i : Bool) : UpperMatˣ := if i then 1 else F

theorem incompatibleTarget_residue (i : Bool) :
    D.q (incompatibleTarget i) = D.q (F^familyDegree i) := by
  cases i <;> decide

theorem each_incompatible_prescription_lifts (i : Bool) :
    ∃ F' : UpperMatˣ, D.q F' = D.q F ∧ F'^familyDegree i = incompatibleTarget i := by
  cases i with
  | false => exact ⟨F,rfl,by simp [familyDegree,incompatibleTarget]⟩
  | true => exact ⟨orderThreeLift,orderThreeLift_residue,orderThreeLift_cube⟩

theorem incompatible_no_shared_frobenius :
    ¬ ∃ F' : UpperMatˣ, D.q F' = D.q F ∧
      ∃ u : Bool → UpperMatˣ, (∀ i, D.q (u i) = 1) ∧
        ∀ i, u i * F'^familyDegree i * (u i)⁻¹ = incompatibleTarget i := by
  rintro ⟨F',_hF,u,_hu,he⟩
  have htrue : (MulAut.conj (u true)) (F'^3) = 1 := he true
  have hc : F'^3=1 := (MulAut.conj (u true)).injective (by simpa using htrue)
  have hfalse : (MulAut.conj (u false)) F' = F := by
    simpa [familyDegree,incompatibleTarget] using he false
  apply provisional_cube_not_one
  rw [← hfalse, ← map_pow, hc, map_one]

theorem incompatible_matching_class_nonzero :
    D.frobeniusMatchingClass F familyDegree incompatibleTarget incompatibleTarget_residue ≠ 0 := by
  intro hz
  exact incompatible_no_shared_frobenius
    ((D.simultaneous_frobenius_matching_iff_class_zero F familyDegree
      incompatibleTarget incompatibleTarget_residue).2 hz)

def compatibleTarget (i : Bool) : UpperMatˣ := if i then 1 else orderThreeLift

theorem compatibleTarget_residue (i : Bool) :
    D.q (compatibleTarget i) = D.q (F^familyDegree i) := by
  cases i <;> decide

theorem compatible_shared_frobenius :
    ∃ F' : UpperMatˣ, D.q F' = D.q F ∧
      ∃ u : Bool → UpperMatˣ, (∀ i, D.q (u i) = 1) ∧
        ∀ i, u i * F'^familyDegree i * (u i)⁻¹ = compatibleTarget i := by
  refine ⟨orderThreeLift,orderThreeLift_residue,fun _ => 1,by intro i; simp,?_⟩
  intro i
  cases i <;> simp [familyDegree,compatibleTarget,orderThreeLift_cube]

theorem compatible_matching_class_zero :
    D.frobeniusMatchingClass F familyDegree compatibleTarget compatibleTarget_residue = 0 :=
  (D.simultaneous_frobenius_matching_iff_class_zero F familyDegree
    compatibleTarget compatibleTarget_residue).1 compatible_shared_frobenius

end Komorebi.StrongArtin.MixedCharacteristic.Examples
