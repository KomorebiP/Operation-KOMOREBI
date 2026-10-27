import AVOC.UpgradeSpecialization
open Komorebi.AVOC
example : 0 ≤ Upgrade.campaignNet (UpgradeCatalogue.authority 100)
    (Upgrade.step (UpgradeCatalogue.authority 100) UpgradeCatalogue.expensiveSearch
      UpgradeCatalogue.goodTrial).next := by
  rw [UpgradeCatalogue.improved_version_unprofitable_campaign.2]
  norm_num
