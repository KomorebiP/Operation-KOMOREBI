import Mathlib.RingTheory.LocalRing.Basic

/-! Paper XII, Proposition 3.4. -/
namespace PaperXII.LocalIdempotents

/-- Every idempotent in a commutative local ring is zero or one. -/
theorem eq_zero_or_one {R : Type*} [CommRing R] [IsLocalRing R]
    (e : R) (he : e * e = e) : e = 0 ∨ e = 1 := by
  rcases IsLocalRing.isUnit_or_isUnit_one_sub_self e with h | h
  · right
    exact h.mul_left_cancel (he.trans (mul_one e).symm)
  · left
    apply h.mul_left_cancel
    calc
      (1 - e) * e = 0 := by rw [sub_mul, one_mul, he, sub_self]
      _ = (1 - e) * 0 := (mul_zero _).symm

end PaperXII.LocalIdempotents
