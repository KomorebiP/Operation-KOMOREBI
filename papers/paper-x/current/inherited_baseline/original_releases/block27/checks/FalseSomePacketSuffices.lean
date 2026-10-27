import PaperX.RequiredPacketBoundary

open PaperX.RequiredPacketBoundary PaperX.JointOccupancy

example : (∃ n, Occupied operator (target 1 n) [()]) →
    ∀ n, Occupied operator (target 1 n) [()] := by
  rw [iff_true_intro some_but_not_all.1, iff_false_intro some_but_not_all.2]
  simp only [true_implies]
