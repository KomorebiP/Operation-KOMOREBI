import AVOC.UpgradeSpecialization
open Komorebi.AVOC
example : (Upgrade.step (UpgradeCatalogue.authority 100) UpgradeCatalogue.initial
    {UpgradeCatalogue.goodTrial with objective := "easier"}).outcome = .promoted := by
  decide
