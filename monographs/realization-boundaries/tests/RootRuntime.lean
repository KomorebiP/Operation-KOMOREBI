import RealizationBoundaries
set_option autoImplicit false
open RealizationBoundaries
#eval (show IO Unit from if certifiedRootSolver (fun p => decide (p.val = 2)) 1 [] 2 = .error 2 then pure () else throw (IO.userError "selected-prime certificate failed"))
#eval (show IO Unit from if rootCorrectionCode (fun _ => false) 0 [0,0,0,1] 2 = [0,0,0,2] then pure () else throw (IO.userError "finite modular correction failed"))
#eval (show IO Unit from if certifiedRootSolver (fun _ => false) 0 [0,0,0,1] 3 = .error 3 then pure () else throw (IO.userError "torsion obstruction failed"))
