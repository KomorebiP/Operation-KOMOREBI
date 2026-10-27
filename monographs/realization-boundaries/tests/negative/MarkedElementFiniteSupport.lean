import tests.Contracts
open RealizationBoundaries RealizationBoundariesSeedTests
set_option autoImplicit false
example (a : ℕ → Bool) : (support (markedElement (pairedSelector a)).val).Finite :=
  marked_not_finite_support a
