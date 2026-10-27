import AVOC
import Mathlib.Tactic.NormNum

open Komorebi.AVOC

/-- Deliberately false: the true-favoring durable archive does not replay to
1/10 mass on `true`; the checked theorem gives 9/10. -/
example :
    (replayArchive uniformBoolBelief retrospectiveTrueArchive
      retrospectiveTrueArchive_positive).prob true = 1 / 10 := by
  rw [retrospectiveTrueArchive_recovers_refined_true]
  norm_num
