import AVOC.SynthesisExamples
open Komorebi.AVOC.Synthesis Komorebi.AVOC.SynthesisExamples
example : searchSpent pairReference 1 85 10000 = 0 := by
  rw [pair_search_charge]
  decide
