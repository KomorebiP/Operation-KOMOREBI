import KomorebiLSM
open Komorebi.LSM.Block2Examples
-- Every completed row annihilates this vector, but the third coordinate does not.
example : thirdRow (0,0,1) = 0 := by norm_num [thirdRow]
