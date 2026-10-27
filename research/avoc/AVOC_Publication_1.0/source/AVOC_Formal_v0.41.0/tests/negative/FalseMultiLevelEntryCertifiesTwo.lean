import AVOC.MultiLevelExamples

open Komorebi.AVOC.MultiLevel.Examples

/-- A nonzero entry certifies rank at least one, not rank at least two. -/
example : afterEntrySuccess.lower = 2 := by
  rw [entry_success_floor]
