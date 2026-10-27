import tests.Contracts
open RealizationBoundaries RealizationBoundariesSeedTests
set_option autoImplicit false
example (a : ℕ → Bool) (S : Set (pairedGroup a)) (h : S.Finite) :
    topologicalEndomorphismHull S = ⊤ := paired_no_finite_topological_seeds a S h
