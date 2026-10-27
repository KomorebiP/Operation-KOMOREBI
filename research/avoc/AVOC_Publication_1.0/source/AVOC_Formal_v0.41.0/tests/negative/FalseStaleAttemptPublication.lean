import AVOC.AttemptExamples
open Komorebi.AVOC.Attempts Komorebi.AVOC.AttemptExamples
example : publish second ⟨0,0,1⟩ = .ok committed := by
  rw [old_attempt_cannot_publish]
