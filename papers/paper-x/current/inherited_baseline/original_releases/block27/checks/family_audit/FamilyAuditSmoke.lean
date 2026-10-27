import PaperX.FamilyClassification
import PaperX.FamilyExamples
import PaperX.FamilyBoundary
set_option autoImplicit false
namespace PaperX.FamilyAuditSmoke
open PaperX.RepresentationLimits PaperX.OrthogonalProjectors
open PaperX.CompletionExamples PaperX.PrecisionExamples
open scoped BigOperators
noncomputable section
abbrev emptyCarrier : MatrixRep ℤ_[2] C2 (Fin 0) := 1
abbrev unaryCarrier : MatrixRep ℤ_[2] C2 (Fin 1) := 1

def emptyInput : Family (reduce twoIdeal emptyCarrier 2) (Fin 0) where
  projector i := Fin.elim0 i
  orthogonal i := Fin.elim0 i
  total := by ext i; exact Fin.elim0 i

def unaryInput : Family (reduce twoIdeal unaryCarrier 2) (Fin 1) where
  projector _ := ⟨1, by simp, by intro g; simp⟩
  orthogonal i j hij := (hij (Subsingleton.elim i j)).elim
  total := by simp

example : ∃ E : Family emptyCarrier (Fin 0), E = E := by
  obtain ⟨E, _⟩ := OrthogonalLifting.exists_family_lift (2 : ℤ_[2]) 1 1
    (by decide) emptyCarrier group_order_nonzero group_order_divides_two emptyInput
  exact ⟨E, rfl⟩

example : ∃ E : Family unaryCarrier (Fin 1),
    (E.projector 0).matrix = 1 := by
  obtain ⟨E, _⟩ := OrthogonalLifting.exists_family_lift (2 : ℤ_[2]) 1 1
    (by decide) unaryCarrier group_order_nonzero group_order_divides_two unaryInput
  exact ⟨E, by simpa using E.total⟩

#print axioms PaperX.OrthogonalLifting.exists_family_lift
#print axioms PaperX.FamilyClassification.exists_family_unique_up_to_conjugacy
#print axioms PaperX.OrthogonalProjectors.Family.decomposition
#print axioms PaperX.FamilyRigidity.exists_conjugating_unit_of_reduction
#print axioms PaperX.FamilyExamples.actual_three_summand_lift
#print axioms PaperX.FamilyExamples.no_exact_family_retains_mod_four
#print axioms PaperX.FamilyBoundary.independent_lifts_not_orthogonal
#print axioms PaperX.FamilyBoundary.generic_rigidity_on_distinct_families
end
end PaperX.FamilyAuditSmoke
