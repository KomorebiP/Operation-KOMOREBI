import AVOC.ResearchControllerExamples
open Komorebi.AVOC.Research Komorebi.AVOC.Research.Examples
example : Allowed demo { initial with budget := 0 } (.attempt 0) := by
  norm_num [Allowed, demo, initial]
