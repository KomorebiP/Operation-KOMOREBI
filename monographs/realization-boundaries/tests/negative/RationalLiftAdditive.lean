import tests.Contracts
open RealizationBoundaries
set_option autoImplicit false
example : rationalDiagonal (pairedSelector (fun _ => false)) ((1/2 : ℚ) + 1/2) =
    rationalDiagonal (pairedSelector (fun _ => false)) (1/2) +
    rationalDiagonal (pairedSelector (fun _ => false)) (1/2) := by
  rfl
