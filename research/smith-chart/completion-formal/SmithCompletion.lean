import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum

/-! Selected algebraic consequences of the two-real-packet Pick criterion. -/
namespace SmithCompletion

noncomputable def diagonalPlus (x y : ℝ) : ℝ := 4 / 3 * (1 - (x + y)^2)
noncomputable def diagonalMinus (x y : ℝ) : ℝ := 4 / 3 * (1 - (x - y)^2)
noncomputable def offDiagonal (x y : ℝ) : ℝ := 4 / 5 * (1 - x^2 + y^2)
noncomputable def determinant (x y : ℝ) : ℝ :=
  diagonalPlus x y * diagonalMinus x y - (offDiagonal x y)^2
def Feasible (x y : ℝ) : Prop :=
  0 ≤ diagonalPlus x y ∧ 0 ≤ diagonalMinus x y ∧ 0 ≤ determinant x y

/-- A zero corner of a nonnegative real block quadratic form forces its cross term to vanish. -/
theorem zero_corner {b d : ℝ} (h : ∀ t : ℝ, 0 ≤ 2 * b * t + d) : b = 0 := by
  by_contra hb
  have h2 : 2 * b ≠ 0 := mul_ne_zero (by norm_num) hb
  have hvalue : 2 * b * (-(d + 1) / (2 * b)) + d = -1 := by
    field_simp [h2]
    ring
  have ht := h (-(d + 1) / (2 * b))
  rw [hvalue] at ht
  norm_num at ht

theorem determinant_factorization (x y : ℝ) :
    determinant x y = 64 / 225 *
      (2 * x^2 - 2 * y^2 - 5 * y - 2) *
      (2 * x^2 - 2 * y^2 + 5 * y - 2) := by
  unfold determinant diagonalPlus diagonalMinus offDiagonal
  ring

theorem saturated_determinant (x : ℝ) :
    determinant x (1/2) = 128 / 225 * x^2 * (2 * x^2 - 5) := by
  rw [determinant_factorization]
  ring

/-- Keeping the maximal odd packet exactly permits no change in the real even packet. -/
theorem saturated_iff (x : ℝ) : Feasible x (1/2) ↔ x = 0 := by
  constructor
  · rintro ⟨hp, hm, hd⟩
    have hbound : x^2 ≤ 3/4 := by
      unfold diagonalPlus at hp
      unfold diagonalMinus at hm
      nlinarith
    by_contra hx
    have hx2 : 0 < x^2 := sq_pos_of_ne_zero hx
    have hnegative : 2 * x^2 - 5 < 0 := by linarith
    have hprod : 128 / 225 * x^2 * (2 * x^2 - 5) < 0 :=
      mul_neg_of_pos_of_neg (mul_pos (by norm_num) hx2) hnegative
    rw [saturated_determinant] at hd
    linarith
  · intro hx
    subst x
    norm_num [Feasible, determinant, diagonalPlus, diagonalMinus, offDiagonal]

theorem incorrect_packet_rejected : determinant (1/10) (1/2) = -1328/46875 := by
  norm_num [determinant, diagonalPlus, diagonalMinus, offDiagonal]

theorem inward_packet_feasible : Feasible (1/10) (49/100) := by
  norm_num [Feasible, determinant, diagonalPlus, diagonalMinus, offDiagonal]

end SmithCompletion
