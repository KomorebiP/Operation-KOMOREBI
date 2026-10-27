import AVOC.AttemptExamples
open Komorebi.AVOC.Attempts Komorebi.AVOC.AttemptExamples
example : ∃ r, renew ⟨10,1⟩ ⟨0,0,1,some ⟨0,0,0⟩,false,false⟩ ⟨0,0,0⟩ = .ok r := by
  rw [count_cap_stops_free_retries]
  exact ⟨initial,rfl⟩
