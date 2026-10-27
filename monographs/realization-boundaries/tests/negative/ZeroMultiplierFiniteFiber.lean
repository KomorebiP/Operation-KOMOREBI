import tests.Contracts

set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesRootTests

example (W : Submodule ℚ TailSpace) : Finite (RootFiber W 0 0) := by
  exact rootFiber_finite W (m := 0) (by decide) 0
