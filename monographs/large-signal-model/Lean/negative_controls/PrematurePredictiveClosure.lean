import KomorebiLSM
open Komorebi.LSM.Block2Examples
-- A first-coordinate-only model loses the incoming second coordinate.
example : firstRow (signalTransition (0,1,0)) = (1/2 : ℚ) * firstRow (0,1,0) := by
  norm_num [firstRow, signalTransition]
