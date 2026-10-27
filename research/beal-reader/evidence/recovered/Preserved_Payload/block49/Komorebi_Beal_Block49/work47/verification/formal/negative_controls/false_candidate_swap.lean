import BealBlock47
example : ∃ candidate : Bool, ∀ test : Bool, candidate = test := by
  exact ⟨false, by intro test; rfl⟩
