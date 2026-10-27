import KomorebiLSM
open Komorebi.LSM.Examples
example : retainFirst (swap (swap (1,0))) =
 retainFirst (swap (retainFirst (swap (retainFirst (1,0))))) := by rfl
