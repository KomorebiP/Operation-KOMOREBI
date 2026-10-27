import ProofPath.ExtensionExamples
-- This is exactly the false negative-observation conjunct of the proposed
-- merged realization. Unfolding the contract is not itself a test failure.
example : ProofPath.ExtensionExamples.target.Extends ({()} : Set Unit) {()}
    (fun _ => True) := by
  refine ⟨?_, ?_, ?_⟩
  · exact ⟨by intro v h; exact False.elim h, by intro j; exact Empty.elim j⟩
  · intro _ _; trivial
  · intro v hv
    change ¬ True
    decide
