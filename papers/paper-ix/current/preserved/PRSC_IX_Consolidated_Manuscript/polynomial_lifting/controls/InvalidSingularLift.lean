module
public import PolynomialControls
@[expose] public section
open Komorebi.PolynomialControls Komorebi.PolynomialObstruction

-- Invalid attempt to infer lifting merely from a singular lower root.
example : ∃ y : Fin 1 → ℤ,
    (∀ i, (2 : ℤ) ∣ y i) ∧
    (∀ i, (4 : ℤ) ∣ evalSystem squareMinusTwo y i) := by
  exact singular_root_without_lift.2.2
