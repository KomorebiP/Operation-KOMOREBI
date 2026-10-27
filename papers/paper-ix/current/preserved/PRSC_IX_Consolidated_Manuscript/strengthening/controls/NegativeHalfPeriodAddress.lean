module
public import DyadicFourSharpening
@[expose] public section
set_option autoImplicit false
open KomorebiPaperIX DyadicFourCongruences
example : (2 : ℤ_[2]) ^ 6 ∣ unnormalizedLift 0 (by decide) (5 + 2 ^ (6 - 2)) -
    unnormalizedLift 0 (by decide) 5 := by
  exact DyadicFourSharpening.half_period 0 6 5 (by decide) (by decide) (by decide) (by decide)
