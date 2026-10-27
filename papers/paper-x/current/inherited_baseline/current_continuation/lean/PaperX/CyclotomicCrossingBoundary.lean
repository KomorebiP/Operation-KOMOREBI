import PaperX.CyclotomicCrossingCore
import Mathlib.Analysis.Complex.Polynomial.Basic

/-!
# A field-level boundary for the restriction-order hypothesis

Complex conjugation over the reals is nontrivial but restricts trivially to
the bottom intermediate field. Its fixed field and that auxiliary field fail
to generate the complex numbers. This is not an arithmetic distribution example.
-/

set_option autoImplicit false

noncomputable section

namespace PaperX.CyclotomicCrossingBoundary

open IntermediateField

/-- The test extension is genuinely a finite Galois extension. -/
theorem real_complex_finite_galois :
    FiniteDimensional ℝ ℂ ∧ IsGalois ℝ ℂ := by
  let : Algebra.IsQuadraticExtension ℝ ℂ := ⟨Complex.finrank_real_complex⟩
  exact ⟨inferInstance, inferInstance⟩

/-- Conjugation is nontrivial on the actual complex field. -/
theorem conjugation_ne_one : Complex.conjAe ≠ 1 := by
  intro h
  have heq := congrArg (fun f : ℂ ≃ₐ[ℝ] ℂ => (f Complex.I).im) h
  norm_num at heq

/-- Its order is two. -/
theorem conjugation_order : orderOf Complex.conjAe = 2 := by
  apply orderOf_eq_prime
  · ext z
    simp [pow_two, AlgEquiv.mul_apply]
  · exact conjugation_ne_one

/-- The auxiliary bottom field sees only the identity restriction. -/
theorem conjugation_restrict_bottom :
    AlgEquiv.restrictNormalHom (⊥ : IntermediateField ℝ ℂ) Complex.conjAe = 1 := by
  apply MonoidHom.mem_ker.mp
  rw [IntermediateField.restrictNormalHom_ker, fixingSubgroup_bot]
  exact Subgroup.mem_top _

/-- In particular, restriction does not preserve the order. -/
theorem conjugation_restriction_order_mismatch :
    orderOf (AlgEquiv.restrictNormalHom (⊥ : IntermediateField ℝ ℂ) Complex.conjAe) ≠
      orderOf Complex.conjAe := by
  rw [conjugation_restrict_bottom, orderOf_one, conjugation_order]
  norm_num

/-- Omitting the restriction-order hypothesis makes the crossing identity false,
even for the concrete finite Galois extension `ℂ/ℝ`. -/
theorem fixed_conjugation_sup_bottom_ne_top :
    fixedField (Subgroup.zpowers Complex.conjAe) ⊔ (⊥ : IntermediateField ℝ ℂ) ≠ ⊤ := by
  rw [sup_bot_eq]
  intro h
  have hI : Complex.I ∈ fixedField (Subgroup.zpowers Complex.conjAe) := by
    rw [h]
    exact mem_top
  have heq := (mem_fixedField_iff (Subgroup.zpowers Complex.conjAe) Complex.I).mp hI Complex.conjAe
    (Subgroup.mem_zpowers Complex.conjAe)
  have him := congrArg Complex.im heq
  norm_num at him

end PaperX.CyclotomicCrossingBoundary
