module
public import PolynomialJointMotionControls
@[expose] public section
open Komorebi.PolynomialJointMotionControls

-- Invalid: in the same actual joint deformation, replacing H(a)+K v with
-- H(a)-K v predicts zero and leaves an error not divisible by 2^4.
example : (2 : ℤ_[2]) ^ 4 ∣ (-8 : ℤ_[2]) - (-(2 : ℤ_[2]) ^ 2 * (1 - 1)) := by
  exact reversed_parameter_sign_fails
