import PaperX.FamilyBoundary
open PaperX.FamilyBoundary
example : leftProjector * skewRight 2 = 0 := by
  rw [iff_false_intro independent_lifts_not_orthogonal]
