import IntrinsicBoundaryConsumers
open PaperIBlock04Tests PaperIBlock03Tests
open Komorebi.PaperICompletion4.OperatorIntrinsicFormula
-- Two nonlinear primary chains have intrinsic dimension two, not one.
example : intrinsicMultiplicity repeatedOperator quadratic = 1 :=
  nonlinear_repeated_intrinsic_dimension_two
