import AVOC.RecoveryExamples
open Komorebi.AVOC Komorebi.AVOC.RecoveryExamples Komorebi.AVOC.PlannerRuntime
example (j : Job) : ∃ d : LiveExecution.StoreView → Nat,
    d (beforeStore j).current = (beforeStore j).next ∧
    d (committedStore j).current = (committedStore j).next := by
  refine ⟨fun _ => 0, rfl, ?_⟩
  change (0 : Nat) = 1
  omega
