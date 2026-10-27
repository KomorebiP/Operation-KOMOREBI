import tests.Contracts

set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesRootTests

example : Nat.card (RootFiber (selectorLine (pairedSelector (fun _ => false))) 2
    (markedElement (pairedSelector (fun _ => false)))) = 2 := by
  exact marked_half_count_zero
