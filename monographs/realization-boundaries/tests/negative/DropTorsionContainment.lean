import RealizationBoundaries
set_option autoImplicit false
noncomputable section
open RealizationBoundaries

example : ∃ W : Submodule ℚ TailSpace, preimage W = (⊥ : AddSubgroup Ambient) := by
  exact ⟨⊥, by rfl⟩
