import AVOC.PlannerExamples
open Komorebi.AVOC ExecutablePlanner PlannerExamples
example : (affordableDepth 4 2 0 3).isSome = true := by
  rw [zero_credit_no_search]
  decide
