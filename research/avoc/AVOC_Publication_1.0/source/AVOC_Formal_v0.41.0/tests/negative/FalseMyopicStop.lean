import AVOC.ResearchControllerExamples
open Komorebi.AVOC Komorebi.AVOC.Research Komorebi.AVOC.Research.Examples
example : Guarded.value (controller demo) 2 initial = 0 := by
  rw [two_step_value_exact]
  norm_num
