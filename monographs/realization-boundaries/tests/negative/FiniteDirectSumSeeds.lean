import tests.Contracts
open RealizationBoundaries RealizationBoundariesSeedTests
set_option autoImplicit false
example (S : Set finiteSupport) (h : S.Finite) : endomorphismHull S = ⊤ :=
  finiteSupport_no_finite_endomorphism_seeds S h
