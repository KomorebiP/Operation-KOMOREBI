import PaperX.QuadraticGaloisPackets
open PaperX.QuadraticGaloisPackets
example : ofRoot (oneRoot ℤ_[2]) = ofRoot (negativeRoot ℤ_[2]) := by
  rw [iff_false_intro dyadic_packets_distinct]
