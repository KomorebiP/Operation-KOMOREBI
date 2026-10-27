module
public import PolynomialJointMotionControls
@[expose] public section
open Komorebi.PolynomialJointMotionControls

-- Invalid: F(Y,T)=Y+T, H=1, p=2, s=0, M=2, a=0, v=1.
-- The prescribed parameter is 4 and the exact solved root is -8.
-- Omitting K v predicts -4 and leaves an error not divisible by 2^4.
example : (2 : ℤ_[2]) ^ 4 ∣ (-8 : ℤ_[2]) - (-(2 : ℤ_[2]) ^ 2 * 1) := by
  exact omitted_parameter_term_fails
