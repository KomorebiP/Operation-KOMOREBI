import tests.Contracts
open RealizationBoundaries
set_option autoImplicit false
example : DiagonalAdmissible (selectorLine (pairedSelector (fun _ => false)))
    (selectorLine (pairedSelector (fun _ => true))) 1 :=
  homDiagonal_admissible _ _
    (0 : pairedGroup (fun _ => false) →+ pairedGroup (fun _ => true))
