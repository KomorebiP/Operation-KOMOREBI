import SimultaneousFrobeniusCriterion
import UnipotentNormExamples

/-! Genuine dual-number matrices: separate roots exist, but shared compatibility
can fail. The general criterion computes the actual inherited cokernel class. -/
noncomputable section
namespace Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples
open Komorebi.StrongArtin.SimultaneousNorm
open UnipotentNormExamples
open GeneralDualMatrix

def exponent (i : Bool) : ℕ := if i then 1 else 0
def degree (i : Bool) : ℕ := 3 ^ exponent i

theorem least_degree (i : Bool) : 3 ^ exponent false ≤ 3 ^ exponent i := by
  cases i <;> decide

/-- Degree 1 and degree 3 must come from the same Frobenius. -/
theorem linear_family_iff (e : Bool → Mat) :
    LocalizationSolvable T degree e ↔ e true = (e false) 1 0 • upper := by
  have hc := primePower_localization_iff_pivot T 3 exponent e false least_degree
  constructor
  · intro hsol
    obtain ⟨_,h⟩ := hc.mp hsol
    have ht := h true
    change e true - ((T-1)^2) (e false) ∈ LinearMap.range ((T-1)^3) at ht
    rw [nilpotent_cube_zero] at ht
    have he : e true - ((T-1)^2) (e false) = 0 := by simpa using ht
    exact (sub_eq_zero.mp he).trans (nilpotent_square_apply _)
  · intro he
    apply hc.mpr
    constructor
    · change e false ∈ LinearMap.range ((T-1)^0)
      simp
    · intro i
      cases i with
      | false =>
        change e false - ((T-1)^0) (e false) ∈ LinearMap.range ((T-1)^1)
        simp
      | true =>
        change e true - ((T-1)^2) (e false) ∈ LinearMap.range ((T-1)^3)
        rw [nilpotent_square_apply,he,sub_self]
        exact Submodule.zero_mem _

def familyTarget (e : Bool → Mat) (i : Bool) : (Matrix n n (Dual k))ˣ :=
  D.kernelUnit ((coordinates k n).symm (e i)) * upperF ^ degree i

theorem familyTarget_residue (e : Bool → Mat) (i : Bool) :
    D.q (familyTarget e i) = D.q (upperF ^ degree i) := by
  change D.q ((D.kernelUnit ((coordinates k n).symm (e i)) : Matrix n n (Dual k)) *
    (upperF ^ degree i : Matrix n n (Dual k))) = _
  rw [map_mul,D.kernelUnit_residue,one_mul]

theorem familyTarget_mismatch (e : Bool → Mat) (i : Bool) :
    coordinates k n (D.unitMismatch (familyTarget e i) (upperF ^ degree i)
      (familyTarget_residue e i)) = e i := by
  have h := D.unitMismatch_kernel_perturbed (upperF^degree i)
    ((coordinates k n).symm (e i)) (familyTarget_residue e i)
  exact (congrArg (coordinates k n) h).trans ((coordinates k n).apply_symm_apply _)

/-- The formula is checked on the actual matching class, not a surrogate. -/
theorem actual_family_class_zero_iff (e : Bool → Mat) :
    D.frobeniusMatchingClass upperF degree (familyTarget e) (familyTarget_residue e) = 0 ↔
      e true = (e false) 1 0 • upper := by
  rw [(linearModel k n F).matchingClass_zero_iff_linear_localization]
  change LocalizationSolvable T degree
    (fun i => coordinates k n (D.unitMismatch (familyTarget e i)
      (upperF^degree i) (familyTarget_residue e i))) ↔ _
  simp only [familyTarget_mismatch]
  exact linear_family_iff e

def incompatibleErrors (i : Bool) : Mat := if i then upper else 0
def compatibleErrors (i : Bool) : Mat := if i then upper else lower

theorem incompatible_each_prescription_lifts (i : Bool) :
    ∃ F' : (Matrix n n (Dual k))ˣ, D.q F' = D.q upperF ∧
      F' ^ degree i = familyTarget incompatibleErrors i := by
  cases i with
  | false =>
    refine ⟨upperF,rfl,?_⟩
    simp [familyTarget,incompatibleErrors,degree,exponent]
  | true =>
    simpa [familyTarget,incompatibleErrors,degree,exponent,UnipotentNormExamples.target]
      using nonzero_upper_mismatch_lifts

theorem incompatible_matching_class_nonzero :
    D.frobeniusMatchingClass upperF degree (familyTarget incompatibleErrors)
      (familyTarget_residue incompatibleErrors) ≠ 0 := by
  intro h
  have he := (actual_family_class_zero_iff incompatibleErrors).mp h
  have hbad : upper = 0 := by simpa [incompatibleErrors] using he
  have hentry := congrArg (fun X : Mat => X 0 1) hbad
  norm_num [upper] at hentry

theorem incompatible_no_shared_frobenius :
    ¬ ∃ F' : (Matrix n n (Dual k))ˣ, D.q F' = D.q upperF ∧
      ∃ u : Bool → (Matrix n n (Dual k))ˣ, (∀ i, D.q (u i) = 1) ∧
        ∀ i, u i * F'^degree i * (u i)⁻¹ = familyTarget incompatibleErrors i := by
  rw [D.simultaneous_frobenius_matching_iff_class_zero]
  exact incompatible_matching_class_nonzero

theorem compatible_matching_class_zero :
    D.frobeniusMatchingClass upperF degree (familyTarget compatibleErrors)
      (familyTarget_residue compatibleErrors) = 0 := by
  apply (actual_family_class_zero_iff compatibleErrors).mpr
  simp [compatibleErrors,lower]

theorem compatible_shared_frobenius_exists :
    ∃ F' : (Matrix n n (Dual k))ˣ, D.q F' = D.q upperF ∧
      ∃ u : Bool → (Matrix n n (Dual k))ˣ, (∀ i, D.q (u i) = 1) ∧
        ∀ i, u i * F'^degree i * (u i)⁻¹ = familyTarget compatibleErrors i := by
  rw [D.simultaneous_frobenius_matching_iff_class_zero]
  exact compatible_matching_class_zero

end Komorebi.StrongArtin.SquareZeroH2.SimultaneousUnipotentExamples
