import AVOC.SemanticSynthesisExamples
open Komorebi.AVOC.SemanticSynthesis
example : (paidSearch 2 0).isSome = true := by
  rw [zero_credit_does_not_search]
  decide
