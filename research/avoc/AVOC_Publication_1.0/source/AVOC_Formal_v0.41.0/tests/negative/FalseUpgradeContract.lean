import AVOC.UpgradeSpecialization
open Komorebi.AVOC
example : (Upgrade.step (UpgradeCatalogue.authority 100) UpgradeCatalogue.initial
    UpgradeCatalogue.badTrial).outcome = .promoted := by
  rw [UpgradeCatalogue.rejected_bad_candidate]
  decide
