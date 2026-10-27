import Mathlib.Tactic.NoncommRing
import Mathlib.Algebra.Ring.Hom.Defs
import Mathlib.Algebra.Ring.Nat
import Mathlib.Tactic.NormNum

/-! Polynomial correction of an approximate idempotent in a possibly
noncommutative ring. No inverse of two is needed. -/
set_option autoImplicit false

namespace PaperX.IdempotentNewton

variable {A B : Type*} [Ring A] [Ring B]

/-- The universal integral polynomial used to correct an idempotent. -/
def correct (a : A) : A := 3 * a ^ 2 - 2 * a ^ 3

/-- The correction changes the input by a multiple of its idempotence error. -/
theorem correct_sub (a : A) :
    correct a - a = -(2 * a - 1) * (a ^ 2 - a) := by
  unfold correct
  simp only [show (2 : A) = 1 + 1 by norm_num,
    show (3 : A) = 1 + 1 + 1 by norm_num]
  noncomm_ring

/-- One correction squares the idempotence error. -/
theorem correct_error (a : A) :
    correct a ^ 2 - correct a =
      (a ^ 2 - a) ^ 2 * (4 * a ^ 2 - 4 * a - 3) := by
  unfold correct
  simp only [show (2 : A) = 1 + 1 by norm_num,
    show (3 : A) = 1 + 1 + 1 by norm_num,
    show (4 : A) = 1 + 1 + 1 + 1 by norm_num]
  noncomm_ring

/-- Polynomial correction fixes exact idempotents. -/
theorem correct_eq_of_idempotent (a : A) (ha : a * a = a) :
    correct a = a := by
  have hz : a ^ 2 - a = 0 := by simp [pow_two, ha]
  have hd := correct_sub a
  rw [hz, mul_zero, sub_eq_zero] at hd
  exact hd

/-- Correction commutes with every unital ring homomorphism. -/
theorem map_correct (f : A →+* B) (a : A) :
    f (correct a) = correct (f a) := by
  unfold correct
  rw [show (2 : A) = 1 + 1 by norm_num,
    show (3 : A) = 1 + 1 + 1 by norm_num]
  simp only [map_sub, map_mul, map_pow, map_add, map_one]
  norm_num

/-- If one matrix intertwines two endomorphisms, it intertwines their powers. -/
theorem pow_intertwines (a b p : A) (h : a * p = p * b) (n : ℕ) :
    a ^ n * p = p * b ^ n := by
  induction n with
  | zero => simp
  | succ n hn =>
      rw [pow_succ', mul_assoc, hn, ← mul_assoc, h, mul_assoc, ← pow_succ']

/-- Polynomial correction preserves every supplied intertwiner. -/
theorem correct_intertwines (a b p : A) (h : a * p = p * b) :
    correct a * p = p * correct b := by
  have h2 := pow_intertwines a b p h 2
  have h3 := pow_intertwines a b p h 3
  unfold correct
  calc
    (3 * a ^ 2 - 2 * a ^ 3) * p =
        3 * (a ^ 2 * p) - 2 * (a ^ 3 * p) := by simp only [sub_mul, mul_assoc]
    _ = 3 * (p * b ^ 2) - 2 * (p * b ^ 3) := by rw [h2, h3]
    _ = p * (3 * b ^ 2 - 2 * b ^ 3) := by
      simp only [show (2 : A) = 1 + 1 by norm_num,
        show (3 : A) = 1 + 1 + 1 by norm_num]
      noncomm_ring

end PaperX.IdempotentNewton
