import H12PrincipalDivisor

namespace H12DivisorCarries
open H12PrincipalDivisor

theorem unit_period_pivot (b c : Int) : pivot (b-15) (c-10) = pivot b c := by
  unfold pivot
  omega

theorem unit_period_weight (c : Int) : weight (c-10) = weight c := by
  unfold weight
  split <;> split <;> omega

theorem finite_window_boundary (b : Int) :
    step (b-15)-step b = -(if 0 < b ∧ b ≤ 15 then (1:Int) else 0) := by
  unfold step
  split <;> split <;> split <;> omega

theorem unit_period_order (a b c : Int) :
    correctionOrder a (b-15) (c-10)-correctionOrder a b c =
    -weight c*(if 0 < b ∧ b ≤ 15 then (1:Int) else 0) := by
  unfold correctionOrder
  rw [unit_period_pivot,unit_period_weight]
  have h := finite_window_boundary b
  unfold wall
  grind

theorem seventh_pivot_carry (b c : Int) :
    pivot (b-8) (c-5) = pivot b c + (if digit b c = 0 then 1 else 0) := by
  have h := digit_range b c
  unfold digit pivot at *
  split <;> omega

theorem seventh_digit_carry (b c : Int) :
    digit (b-8) (c-5) = (digit b c+6)%7 := by
  have h := digit_range b c
  have hn := digit_range (b-8) (c-5)
  have p := seventh_pivot_carry b c
  unfold digit at *
  split at p <;> omega

end H12DivisorCarries
