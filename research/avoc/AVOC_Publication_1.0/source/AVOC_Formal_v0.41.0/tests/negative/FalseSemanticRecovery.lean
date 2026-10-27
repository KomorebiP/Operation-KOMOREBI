import AVOC.VerifierExamples

namespace Komorebi.AVOC

/-- Deliberately false: a one-point formal specification cannot recover both
Boolean intended states. -/
example :
    ∃ downstream : Unit → Bool,
      RecoversThrough eraseBoolSpecification id downstream := by
  refine ⟨fun _ => false, ?_⟩
  intro b
  cases b <;> rfl

end Komorebi.AVOC
