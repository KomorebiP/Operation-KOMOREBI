import tests.Contracts
open RealizationBoundaries RealizationBoundariesSeedTests
set_option autoImplicit false
example : AddSubgroup.closure {(1 : Ambient)} = ⊤ := ambient_topological_generator
