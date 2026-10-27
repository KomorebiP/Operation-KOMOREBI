module
public import PolynomialWeightedControls
@[expose] public section
open Komorebi.PolynomialWeightedControls MvPolynomial

-- Invalid: allowing r = 2s would force a root for X^2 + 3 at p = 2.
-- The checked positive control proves no p-adic input is a root.
example : ∃ a : Fin 1 → ℤ_[2], eval a squarePlusThree = 0 := by
  exact boundary_no_root
