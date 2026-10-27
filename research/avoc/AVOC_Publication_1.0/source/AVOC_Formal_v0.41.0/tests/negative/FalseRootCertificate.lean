import AVOC.ResearchControllerExamples
open Komorebi.AVOC Komorebi.AVOC.Research.Examples
example : Scheduling.LocalRule (fun _ : Fin 1 => False) 0 := by
  rw [iff_false_intro false_root_rule_impossible]
  trivial
