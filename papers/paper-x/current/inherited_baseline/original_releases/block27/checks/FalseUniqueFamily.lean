import PaperX.FamilyBoundary
open PaperX.FamilyBoundary
example : splitFamily 2 = splitFamily 0 := by
  rw [iff_false_intro complete_families_distinct]
