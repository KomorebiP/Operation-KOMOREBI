import AVOC.DurableUpgradeExamples
open Komorebi.AVOC.DurableUpgradeExamples
example : afterReserve.current.evaluationSpent = 0 := by
  rw [reserve_is_paid_not_promoted.1]
  decide
