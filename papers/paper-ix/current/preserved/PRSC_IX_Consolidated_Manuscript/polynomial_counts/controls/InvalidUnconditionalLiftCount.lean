module
public import PolynomialCountControls
@[expose] public section
open Komorebi.PolynomialCountControls Komorebi.PolynomialLiftCounts

-- Invalid: rank-nullity's nonzero count cannot ignore the residual obstruction.
example : Nat.card (ActualLifts 2 1 squareMinusTwo (fun _ => 0)) = 2 := by
  exact obstructed_square_lift_count
