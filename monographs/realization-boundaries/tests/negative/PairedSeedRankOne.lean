import tests.Contracts
open RealizationBoundaries RealizationBoundariesSeedTests
set_option autoImplicit false
example (a : ℕ → Bool) : endomorphismSeedRank (pairedGroup a) = 1 :=
  paired_endomorphismSeedRank a
