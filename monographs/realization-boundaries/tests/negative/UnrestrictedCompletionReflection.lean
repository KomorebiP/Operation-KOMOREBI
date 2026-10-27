import tests.Contracts
open RealizationBoundaries RealizationBoundariesDiagonalTests
set_option autoImplicit false
example (a : ℕ → Bool) : Function.Bijective (bottomInclusion a) :=
  bottomInclusion_completion_bijective a
