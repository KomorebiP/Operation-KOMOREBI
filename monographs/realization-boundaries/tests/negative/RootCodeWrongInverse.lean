import RealizationBoundaries
set_option autoImplicit false
open RealizationBoundaries
#eval (show IO Unit from if rootCorrectionCode (fun _ => false) 0 [0,0,0,1] 2 = [0,0,0,1] then pure () else throw (IO.userError "ROOT_EXPECTATION_FALSE"))
