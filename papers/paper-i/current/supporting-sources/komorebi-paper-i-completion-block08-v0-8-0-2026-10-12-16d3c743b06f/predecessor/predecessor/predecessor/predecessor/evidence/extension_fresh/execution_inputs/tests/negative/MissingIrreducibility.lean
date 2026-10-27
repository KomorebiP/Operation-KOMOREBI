import IntrinsicBoundaryConsumers
open Polynomial PaperIBlock04Tests
open Komorebi.PaperICompletion4.OperatorIntrinsicFormula
-- Irreducibility of X cannot stand in for irreducibility of the zero polynomial.
#check operatorPrimaryQuotientEquiv repeatedPresentation (0 : ℚ[X])
  (irreducible_X : Irreducible (X : ℚ[X]))
