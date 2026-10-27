import RealizationBoundaries
set_option autoImplicit false
open RealizationBoundaries
#eval (show IO Unit from if certifiedRootSolver (fun _ => false) 0 [0,0,0,1] 3 = .ok (0,[]) then pure () else throw (IO.userError "ROOT_EXPECTATION_FALSE"))
