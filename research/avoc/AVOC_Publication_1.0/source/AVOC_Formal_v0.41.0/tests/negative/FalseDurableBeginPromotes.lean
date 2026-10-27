import AVOC.DurableUpgradeExamples
open Komorebi.AVOC.DurableUpgradeExamples Komorebi.AVOC.UpgradeCatalogue
example : afterReserve.current.active = Version.threshold := by
  rw [reserve_is_paid_not_promoted.2.1]
  decide
