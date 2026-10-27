import PaperX.RequiredPacketBoundary

open PaperX.RequiredPacketBoundary PaperX.JointOccupancy

example : Occupied operator (target 1 0) [()] := prefix_occupied 1 0 (by decide)
example : ¬ Occupied operator (target 1 1) [()] := omitted_packet_empty 1
example : LinearMap.trace ℚ (Fin 1 → ℚ) (joint operator (target 8 3) [()]) = 1 := by
  simpa using projector_trace 8 3
example : LinearMap.trace ℚ (Fin 1 → ℚ) (joint operator (target 8 8) [()]) = 0 := by
  simpa using projector_trace 8 8
example : (∀ n < 0, Occupied operator (target 0 n) [()]) ∧
    ¬ Occupied operator (target 0 0) [()] := finite_prefix_misses_failure 0
example (s : Finset ℕ) :
    ∃ N, (∀ n ∈ s, Occupied operator (target N n) [()]) ∧
      ¬ Occupied operator (target N N) [()] := finite_sample_misses_failure s
