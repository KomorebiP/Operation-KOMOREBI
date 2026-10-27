import AVOC.SynthesisExamples
open Komorebi.AVOC.Synthesis Komorebi.AVOC.SynthesisExamples
example : 0 ≤ (campaign pairReference 1 100000 1 85 10000).net := by
  rw [better_program_unprofitable_search]
  decide
