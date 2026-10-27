import RealizationBoundaries
set_option autoImplicit false
noncomputable section
open RealizationBoundaries

example (W : Submodule ℚ TailSpace) : Countable (preimage W) := by
  infer_instance
