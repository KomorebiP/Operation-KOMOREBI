import AVOC.ResearchControllerExamples
open Komorebi.AVOC.Research.Examples
example : (0 : Fin 1) ∈ afterSignal.completed := by
  change (0 : Fin 1) ∈ (∅ : Finset (Fin 1))
  simp
