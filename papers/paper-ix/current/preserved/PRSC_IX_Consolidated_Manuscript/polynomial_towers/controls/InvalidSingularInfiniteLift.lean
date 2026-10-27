module
public import PolynomialTowerControls
@[expose] public section
open Komorebi.PolynomialTowerControls

-- Invalid: the singular root one lifts through modulus four but has no root at modulus eight.
example : ∃ z : ℕ → Fin 1 → ℤ,
    ∀ n i, (2 : ℤ)^(1+n) ∣ MvPolynomial.eval (z n) (squareMinusFive i) := by
  exact square_minus_five_no_tower
