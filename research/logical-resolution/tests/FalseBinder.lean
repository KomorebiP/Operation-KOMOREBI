module
public import StandardTranslation
open Komorebi.LogicalResolution.Standard
-- The newest binder is level 1, not level 0.
example : pushMap (α:=Empty) (fun _ : Fin 1 => Sum.inr (0 : Fin 1)) (0 : Fin 2) =
    Sum.inr (0 : Fin 2) := by rfl
