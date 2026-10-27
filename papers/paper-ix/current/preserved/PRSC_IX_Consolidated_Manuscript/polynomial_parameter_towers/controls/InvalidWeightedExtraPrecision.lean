module
public import PolynomialWeightedControls
@[expose] public section
open Komorebi.PolynomialWeightedControls

-- Invalid: the exact shifted root of 2X + 8 is -4, with depth two.
-- The weighted estimate r-s = 3-1 = 2 cannot uniformly gain another digit.
example : (2 : ℤ_[2]) ^ (3 - 1 + 1) ∣ -(2 : ℤ_[2]) ^ (3 - 1) := by
  exact (linear_displacement_sharp 2 1 3).2
