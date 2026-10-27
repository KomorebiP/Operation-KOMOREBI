import PaperX.QuadraticPacketBoundary
open PaperX.QuadraticPacketBoundary
example : (3 : ZMod 8) = 1 ∨ (3 : ZMod 8) = -1 := by
  have h : ¬ ((3 : ZMod 8) = 1 ∨ (3 : ZMod 8) = -1) := by
    rintro (h | h)
    · exact three_not_sign_mod_eight.1 h
    · exact three_not_sign_mod_eight.2 h
  rw [iff_false_intro h]
