import AVOC.DurableUpgradeExamples
open Komorebi.AVOC.DurableUpgradeExamples Komorebi.AVOC.DurableUpgrade
open Komorebi.AVOC.UpgradeCatalogue
example : replay (authority 100) start [.begin good, .finish good.key] = .ok final := by
  rw [omitted_failed_trial_is_rejected]
  contradiction
