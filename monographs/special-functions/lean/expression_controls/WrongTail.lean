import CoupledExpressionRefinement
open Komorebi.SpecialFunctions.Coupled.Scales.Python.Expressions
example : evalRat (env [("last",0)] [("majorant",1),("x",1),("s",2)]) Source.tail = (1/2 : ℚ) := by
  norm_num [evalRat,evalNat,env,Source.tail]
