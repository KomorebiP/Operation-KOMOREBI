import AVOC.Core

namespace Komorebi.AVOC.Negative

def eraseBool : Bool → Unit := fun _ => ()

def boolTarget : Bool → Bool := id

/-- DELIBERATELY FALSE. The proof must fail at the `true` case because a
constant representation cannot recover the identity target. -/
example : TaskSufficient eraseBool boolTarget := by
  refine ⟨fun _ => false, ?_⟩
  intro x
  cases x <;> rfl

end Komorebi.AVOC.Negative
