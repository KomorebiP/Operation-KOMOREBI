module
public import DyadicIsometryControls

open KomorebiPaperIX

example : DyadicFourIsometry.isometry 0 (by decide) (1 : ℤ_[2]) = 1 := by
  simpa using DyadicIsometryControls.address_zero_at_one
