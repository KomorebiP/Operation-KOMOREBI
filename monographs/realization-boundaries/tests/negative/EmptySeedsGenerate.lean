import tests.Contracts
open RealizationBoundaries RealizationBoundariesSeedTests
set_option autoImplicit false
example : ordinaryTopologicalHull (∅ : Set Ambient) = ⊤ := empty_ambient_not_generating
