module
public import DyadicFourLeastPeriods
@[expose] public section
set_option autoImplicit false
open KomorebiPaperIX
example : Congruential.unnormalized 4 0 (0 + 0) - Congruential.unnormalized 4 0 0 ≠ 0 := by
  exact (DyadicFourLeastPeriods.exact_displacement 0 0 0 (by decide) (by decide)).1
