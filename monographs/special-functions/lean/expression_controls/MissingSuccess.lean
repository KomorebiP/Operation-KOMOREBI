import CoupledExpressionRefinement
open Komorebi.SpecialFunctions.Coupled.Scales
open Komorebi.SpecialFunctions.Coupled.Scales.Python
open Komorebi.SpecialFunctions.Coupled.Scales.Python.Expressions
example (p : RationalScales) (x : ℚ) (last : Option ℕ) (outer : Option ℚ) (v : EvaluationResult) :
    expressionResult p v.x v.last_index v.outer_radius v.majorant = encode v := by
  exact expression_result_success p x last outer v
