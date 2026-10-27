module
public import PolynomialParameterControls
@[expose] public section
open Komorebi.PolynomialParameterControls Komorebi.PolynomialPadicLift

-- Full Jacobian surjectivity does not allow an arbitrary prescribed solved block.
-- X^2-T is smooth at the origin modulo two, but T=2 has no p-adic root.
example : ∃ a : Fin (1+1) → ℤ_[2],
    padicEval 2 squareMinusParameter a = 0 ∧ a 1 = 2 := by
  exact no_root_at_parameter_two
