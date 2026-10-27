import AVOC.SynthesisExamples
open Komorebi.AVOC.Synthesis Komorebi.AVOC.SynthesisExamples
example : nodes (synthesize pairReference 2 21845 0) < nodes pairReference := by
  rw [zero_credit_retains_reference]
  decide
