import AVOC.ModelBridgeExamples
open Komorebi.AVOC.Guarded Komorebi.AVOC.ModelBridgeExamples
example (s : BState) : value rawSystem 1 s -
    planValue rawSystem s (policyPlan rawSystem (fun _ _ => true) 1 s) = 0 := by
  rw [example_actual_regret]
  norm_num
