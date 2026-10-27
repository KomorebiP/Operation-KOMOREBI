import RealizationBoundaries
set_option autoImplicit false
open RealizationBoundaries
#eval (show IO Unit from if certifiedRootSolver (fun p => decide (p.val = 2)) 1 [] 2 = .ok (1/2,[]) then pure () else throw (IO.userError "ROOT_EXPECTATION_FALSE"))
