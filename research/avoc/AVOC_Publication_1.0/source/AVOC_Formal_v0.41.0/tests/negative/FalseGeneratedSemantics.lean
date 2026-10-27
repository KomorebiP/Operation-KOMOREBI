import AVOC.SynthesisExamples
open Komorebi.AVOC.Synthesis Komorebi.AVOC.SynthesisExamples
example : check (.literal true) pairReference = true := by
  rw [protected_function_not_constant]
  decide
