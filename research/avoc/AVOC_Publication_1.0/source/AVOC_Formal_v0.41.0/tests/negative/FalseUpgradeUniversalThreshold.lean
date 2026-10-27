import AVOC.UpgradeSpecialization
import AVOC.RetryExamples
open Komorebi.AVOC
example : (UpgradeCatalogue.execute .threshold RetryExamples.improving 2 false).retry =
    (UpgradeCatalogue.execute .dynamic RetryExamples.improving 2 false).retry := by
  norm_num [UpgradeCatalogue.execute, Retry.evaluate, Retry.immediate, RetryExamples.improving]
