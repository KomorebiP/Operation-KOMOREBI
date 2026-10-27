import GeometricBoundaryConsumers
open PaperIBlock05Tests Komorebi.PaperICompletion5.LinearPrimaryEigenspace Polynomial
example : Function.Injective (polynomialCokernelMap jordanOperator X) :=
  polynomialCokernelMap_surjective jordanOperator X
