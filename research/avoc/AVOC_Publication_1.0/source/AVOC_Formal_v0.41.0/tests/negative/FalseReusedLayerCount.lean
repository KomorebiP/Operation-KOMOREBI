import AVOC.SemanticSynthesisExamples
open Komorebi.AVOC.Synthesis Komorebi.AVOC.SemanticSynthesis
example : (expand (codes (representatives 1))).length = (programs 2).length := by
  rw [feedback_second_layer_count, frozen_second_layer_count]
  decide
