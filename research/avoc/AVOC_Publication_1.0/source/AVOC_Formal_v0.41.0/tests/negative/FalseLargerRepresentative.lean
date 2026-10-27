import AVOC.SemanticSynthesisExamples
open Komorebi.AVOC.Synthesis Komorebi.AVOC.SemanticSynthesis
example : nodes (.neg (.neg sx)) ≤ nodes sx := by decide
