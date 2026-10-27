import AVOC.SemanticSynthesisExamples
open Komorebi.AVOC.Synthesis Komorebi.AVOC.SemanticSynthesis
example : run sx ⟨true,false,false⟩ = run (.literal false) ⟨true,false,false⟩ := by decide
