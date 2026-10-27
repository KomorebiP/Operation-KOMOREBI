import AVOC.MultiLevelExamples

open Komorebi.AVOC.MultiLevel.Examples

/-- A negative rank-probe report filters the catalogue but does not create a
positive algebraic certificate. -/
example : afterMinorFailure.lower = 2 := by
  rw [minor_failure_floor]
