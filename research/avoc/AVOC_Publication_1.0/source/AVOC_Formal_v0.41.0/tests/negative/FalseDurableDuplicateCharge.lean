import AVOC.DurableUpgradeExamples
open Komorebi.AVOC.DurableUpgradeExamples Komorebi.AVOC.DurableUpgrade
open Komorebi.AVOC.UpgradeCatalogue
example : finish (authority 100) final good.key = .ok ⟨final, true, 3, 1⟩ := by
  rw [duplicate_promotion_has_no_debit]
  decide
