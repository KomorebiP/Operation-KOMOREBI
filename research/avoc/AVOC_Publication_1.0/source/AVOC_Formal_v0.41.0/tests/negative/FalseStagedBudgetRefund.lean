import AVOC.StagedAffineExamples
open Komorebi.AVOC.Affine.StagedExamples
example : warmReady.budget = 196 := by
  have h := staged_budget_after_warm.1
  omega
