import PaperX.RequiredPacketBoundary

open PaperX.RequiredPacketBoundary PaperX.JointOccupancy

example : ∀ N, (∀ n < N, Occupied operator (target N n) [()]) →
    ∀ n, Occupied operator (target N n) [()] := by
  intro N
  rw [iff_true_intro (finite_prefix_misses_failure N).1,
    iff_false_intro (no_family_fully_occupied N)]
  simp only [true_implies]
