import tests.Contracts

set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesRootTests

example (W : Submodule ℚ TailSpace) : ∃! y : preimage W, (4 : ℕ) • y = 0 := by
  apply (unique_root_iff_one W (by decide : 0 < 4) 0 ⟨0, nsmul_zero 4⟩).mpr
  decide
