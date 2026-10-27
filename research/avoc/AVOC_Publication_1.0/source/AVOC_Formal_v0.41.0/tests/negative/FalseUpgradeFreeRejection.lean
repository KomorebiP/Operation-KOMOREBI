import AVOC.UpgradeSpecialization
open Komorebi.AVOC
example : UpgradeCatalogue.beforeUpgrade.evaluationSpent = 0 := by
  rw [UpgradeCatalogue.bad_trial_cost_retained]
  decide
