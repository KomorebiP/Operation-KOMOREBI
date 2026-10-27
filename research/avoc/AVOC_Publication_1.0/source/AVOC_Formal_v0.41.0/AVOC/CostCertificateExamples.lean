import AVOC.SemanticLibrary

namespace Komorebi.AVOC.CostCertificateExamples

open Synthesis CostCertificate BoolClosure SemanticLibrary

/-- This algebra makes clear why lower inequalities alone do not give witnesses. -/
def unitAlgebra : Algebra Unit where
  literal _ := ()
  atom _ := ()
  neg _ := ()
  conj _ _ := ()
  disj _ _ := ()
  excl _ _ := ()

theorem zero_is_lower : LowerValid unitAlgebra (fun _ => 0) := by
  constructor <;> intros <;> decide

theorem zero_has_no_realizer (w : Unit → Program) :
    ¬ Realizes unitAlgebra (fun _ => 0) w := by
  intro h
  have he := (h ()).2
  change nodes (w ()) = 0 at he
  have hp := nodes_positive (w ())
  omega

def paddedUnit (_ : Unit) : Program := .neg (.literal false)

theorem valid_witness_can_be_nonminimal :
    Realizes unitAlgebra (fun _ => 2) paddedUnit := by
  intro s
  cases s
  exact ⟨rfl,rfl⟩

theorem witness_cost_two_not_lower : ¬ LowerValid unitAlgebra (fun _ => 2) := by
  intro h
  have bad := h.literal false
  change 2 ≤ 1 at bad
  omega

theorem empty_bank_rejected : checkBank #[] = false := by decide

theorem unfunded_empty_bank_no_charge : (paidImport #[] 0).charged = 0 := by decide

theorem funded_empty_bank_charged :
    (paidImport #[] 200000).charged = closureObligations := by decide

theorem false_same_semantics : ¬ Equivalent (.literal false) (.literal true) := by
  intro h
  have bad := h ⟨false,false,false⟩
  change false = true at bad
  contradiction

end Komorebi.AVOC.CostCertificateExamples
