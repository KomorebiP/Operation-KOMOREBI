import tests.Contracts

set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesRootTests

example (W : Submodule ℚ TailSpace) : (preimage W ⧸ multiples W 4) ≃+ ZMod 4 := by
  exact (cyclicIntegerQuotientEquiv W (by decide : 0 < 4)).trans
    (ZMod.ringEquivCongr radical_four).toAddEquiv
