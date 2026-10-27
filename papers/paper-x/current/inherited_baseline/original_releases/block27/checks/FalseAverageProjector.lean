import PaperX.SummandBoundary
open PaperX.SummandBoundary
example : rationalAverage * rationalAverage = rationalAverage := by
  rw [iff_false_intro rational_average_not_idempotent]
