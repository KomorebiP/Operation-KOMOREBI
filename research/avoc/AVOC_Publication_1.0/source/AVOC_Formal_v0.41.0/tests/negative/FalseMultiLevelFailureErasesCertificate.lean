import AVOC.MultiLevelExamples

open Komorebi.AVOC.MultiLevel
open Komorebi.AVOC.MultiLevel.Examples

/-- Later negative information cannot erase an already certified rank floor. -/
example : (afterFailure model afterMinorSuccess 0).lower = 0 := by
  rw [failure_preserves_floor, minor_success_floor]
