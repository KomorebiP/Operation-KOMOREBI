import CoupledExpressionRefinement
open Komorebi.SpecialFunctions.Coupled.Scales.Python.Expressions
example : evalNat (env [("n",1),("i",0)]) Source.r_power = 0 := by
  norm_num [evalNat,env,Source.r_power]
