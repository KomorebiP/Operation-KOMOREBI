import tests.Contracts
open RealizationBoundaries RealizationBoundariesDiagonalTests
set_option autoImplicit false
example (U V : Submodule ℚ TailSpace) (f : preimage U →+ preimage V)
    (p q : Prime) (hpq : p ≠ q) : (f (preimageSeed U p)).val q = 1 :=
  no_off_diagonal_seed U V f p q hpq
