import PaperX.QuadraticLocalArithmetic
open PaperX.QuadraticGaloisInertia PaperX.QuadraticLocalPackets
open PaperX.QuadraticGaloisPackets PaperX.QuadraticLocalArithmetic
example : InertiaTrivial 3 (ofRoot (negativeRoot ℤ_[2])) ↔
    LocallyTrivial ℚ_[3] (ofRoot (negativeRoot ℤ_[2])) := by
  rw [iff_true_intro sign_inertiaTrivial_three,
    iff_false_intro sign_not_locallyTrivial_three]
  simp only [true_iff]
