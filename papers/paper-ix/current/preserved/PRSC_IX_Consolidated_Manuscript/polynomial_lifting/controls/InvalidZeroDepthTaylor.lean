module
public import PolynomialControls
@[expose] public section
open Komorebi.PolynomialControls

-- Invalid attempt to erase the positive-depth hypothesis.
example : (2 : ℤ) ∣
    MvPolynomial.eval (fun _ : Fin 1 => (1 : ℤ)) squarePolynomial -
      MvPolynomial.eval (fun _ : Fin 1 => (0 : ℤ)) squarePolynomial -
      Komorebi.PolynomialTaylor.directional squarePolynomial (fun _ => 0) (fun _ => 1) := by
  exact zero_depth_taylor_failure
