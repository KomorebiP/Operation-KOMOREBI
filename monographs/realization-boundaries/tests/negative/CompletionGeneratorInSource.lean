import tests.Contracts
open RealizationBoundaries RealizationBoundariesSeedTests
set_option autoImplicit false
example (a : ℕ → Bool) : completionGenerator (selectorLine (pairedSelector a)) ∈
    Set.range (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (pairedGroup a))) :=
  paired_completionGenerator_not_in_eta_range a
