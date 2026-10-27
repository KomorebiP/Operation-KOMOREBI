module
public import PolynomialMotionControls
@[expose] public section
open Komorebi.PolynomialMotionControls

-- Invalid: for F=X+X^2, H=1, p=2, s=0, M=1, the root exists in 2 Z_2,
-- and its first-order error b+2 has exactly depth two, not depth three.
example : ∀ b : ℤ_[2], b + b ^ 2 + 2 = 0 → (2 : ℤ_[2]) ∣ b →
    (2 : ℤ_[2]) ^ 3 ∣ b + 2 := by
  exact no_uniform_extra_error_digit
