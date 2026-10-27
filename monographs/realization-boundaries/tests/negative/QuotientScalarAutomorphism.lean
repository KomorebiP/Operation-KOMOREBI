import tests.Contracts
open RealizationBoundaries RealizationBoundariesDiagonalTests
set_option autoImplicit false
example (a : ℕ → Bool) : Function.Bijective (selectedProjection a) :=
  (selector_hom_bijective_iff _ _ (pairedSelector_infinite a) (selectedProjection a)).mpr
    (selectedProjection_scalar a)
