module
public import PolynomialControls
@[expose] public section
open Komorebi.PolynomialControls Komorebi.PolynomialObstruction

-- Invalid attempt to merge two separate polynomial lifts into a common lift.
example : ∃ y : Fin 1 → ℤ,
    (∀ i, (2 : ℤ) ∣ y i) ∧
    (∀ i, (4 : ℤ) ∣ evalSystem linearZero y i) ∧
    (∀ i, (4 : ℤ) ∣ evalSystem linearTwo y i) := by
  exact separate_polynomial_lifts
