module
public import PolynomialTowerControls
@[expose] public section
open Komorebi.PolynomialTowerControls

-- Invalid: the nonsingular root zero modulo two for X−2 cannot keep zero modulo four.
example : ∃ y : Fin 1 → ℤ,
    MvPolynomial.eval y (linearMinusTwo 0) = 0 ∧ (4 : ℤ) ∣ y 0 := by
  exact linear_shift_no_extra_precision
