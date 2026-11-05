import CoupledExpressionRefinement
open Komorebi.SpecialFunctions.Coupled.Scales.Python.Expressions
#check product_expression_lowering
#check dictionary_expression_lowering
#check source_return_interpreted
example : evalNat (env) Source.steps_default = 20 := rfl
example : evalNat (env [("n",1),("i",0)]) Source.r_power = 1 := rfl
