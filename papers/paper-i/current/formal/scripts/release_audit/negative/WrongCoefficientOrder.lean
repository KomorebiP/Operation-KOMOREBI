-- Deliberate negative control: division coefficients have a specified side.
import Mathlib.Algebra.Quaternion
set_option autoImplicit false
example (a b : Quaternion ℚ) (hb : b ≠ 0) : (b⁻¹ * a) * b = a := by
  exact div_mul_cancel₀ a hb
