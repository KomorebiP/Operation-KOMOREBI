module
public import PolynomialCountControls
@[expose] public section
open Komorebi.PolynomialCountControls Komorebi.PolynomialLiftCounts

-- Invalid: a liftable singular root need not have a unique next-level lift.
example : Nat.card (ActualLifts 2 1 squareSystem (fun _ => 0)) = 1 := by
  exact singular_square_lift_count
