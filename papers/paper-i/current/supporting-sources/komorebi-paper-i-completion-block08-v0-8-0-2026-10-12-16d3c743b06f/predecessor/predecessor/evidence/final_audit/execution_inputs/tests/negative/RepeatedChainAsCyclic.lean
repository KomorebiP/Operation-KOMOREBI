import ScalarExtensionBoundaryConsumers
open Komorebi.SingleOperatorGraph
example : HasCyclicVector (PaperIBlock05Tests.repeatedJordanOperator.baseChange (AlgebraicClosure ℂ)) :=
  PaperIBlock06Tests.squared_extended_cyclic
