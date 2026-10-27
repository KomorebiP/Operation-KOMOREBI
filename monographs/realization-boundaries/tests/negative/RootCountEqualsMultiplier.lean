import tests.Contracts

set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesRootTests

example (W : Submodule ℚ TailSpace) : Nat.card (RootFiber W 4 0) = 4 := by
  exact fourth_zero_has_two_roots W
