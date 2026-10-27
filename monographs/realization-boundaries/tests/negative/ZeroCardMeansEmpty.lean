import tests.Contracts

set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesRootTests

example (W : Submodule ℚ TailSpace) : IsEmpty (RootFiber W 0 0) := by
  exact Nat.card_eq_zero.mp (zeroRootFiber_card W)
