import PaperX.QuadraticLocalArithmetic
open PaperX.QuadraticLocalPackets PaperX.QuadraticGaloisPackets
example : LocallyTrivial ℚ_[3] (ofRoot (negativeRoot ℤ_[2])) := by
  rw [iff_false_intro PaperX.QuadraticLocalArithmetic.sign_not_locallyTrivial_three]
