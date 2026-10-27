import Komorebi.SufficientResolution.ApproximateBounds
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.FieldSimp

/-!
# Exact scalar response kernel and stable bounds

The two-rate response avoids division, including equal or zero rates. It is the
convolution majorant for one-step errors transported between two models.
-/

set_option autoImplicit false

namespace Komorebi.SufficientResolution.ScalarBudgets

open ApproximateBounds

universe uI
variable {I : Type uI}

/-- Two growth rates, one defect injection at each step. -/
def response (a b : ℝ) : ℕ → ℝ
  | 0 => 0
  | n + 1 => a * response a b n + b ^ n

@[simp] theorem response_zero (a b : ℝ) : response a b 0 = 0 := rfl

@[simp] theorem response_one (a b : ℝ) : response a b 1 = 1 := by
  simp [response]

theorem response_succ (a b : ℝ) (n : ℕ) :
    response a b (n + 1) = a * response a b n + b ^ n := rfl

theorem response_nonneg (a b : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b) (n : ℕ) :
    0 ≤ response a b n := by
  induction n with
  | zero => rfl
  | succ n ih => exact add_nonneg (mul_nonneg ha ih) (pow_nonneg hb n)

/-- Division-free geometric identity; valid also when a=b. -/
theorem response_mul_sub (a b : ℝ) (n : ℕ) :
    (a - b) * response a b n = a ^ n - b ^ n := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [response_succ, pow_succ, pow_succ]
    calc
      (a - b) * (a * response a b n + b ^ n) =
          a * ((a - b) * response a b n) + (a - b) * b ^ n := by ring
      _ = a * (a ^ n - b ^ n) + (a - b) * b ^ n := by rw [ih]
      _ = a ^ n * a - b ^ n * b := by ring

/-- The opposite recurrence is often the useful one for contraction estimates. -/
theorem response_succ_right (a b : ℝ) (n : ℕ) :
    response a b (n + 1) = b * response a b n + a ^ n := by
  rw [response_succ]
  nlinarith [response_mul_sub a b n]

theorem response_swap (a b : ℝ) (n : ℕ) : response a b n = response b a n := by
  induction n with
  | zero => rfl
  | succ n ih => rw [response_succ, response_succ_right b a, ih]

/-- Finite path convolution, indexed without negative or partial exponents. -/
theorem response_eq_sum (a b : ℝ) (n : ℕ) :
    response a b n = ∑ j ∈ Finset.range n, a ^ j * b ^ (n - 1 - j) := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [response_succ, ih, Finset.sum_range_succ']
    have h : ∑ j ∈ Finset.range n, a ^ (j + 1) * b ^ (n + 1 - 1 - (j + 1)) =
        a * ∑ j ∈ Finset.range n, a ^ j * b ^ (n - 1 - j) := by
      rw [Finset.mul_sum]
      apply Finset.sum_congr rfl
      intro j hj
      have he : n + 1 - 1 - (j + 1) = n - 1 - j := by omega
      rw [he, pow_succ]
      ring
    rw [h]
    simp

theorem response_of_ne (a b : ℝ) (h : a ≠ b) (n : ℕ) :
    response a b n = (a ^ n - b ^ n) / (a - b) := by
  apply (eq_div_iff (sub_ne_zero.mpr h)).2
  nlinarith [response_mul_sub a b n]

/-- Equal-rate formula, including rate zero and the first step. -/
theorem response_same_succ (a : ℝ) (n : ℕ) :
    response a a (n + 1) = (n + 1 : ℕ) * a ^ n := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [response_succ, ih, pow_succ]
    push_cast
    ring

@[simp] theorem response_one_one (n : ℕ) : response 1 1 n = n := by
  cases n with
  | zero => simp
  | succ n => simp [response_same_succ]

theorem response_mono (a b a' b' : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b)
    (haa : a ≤ a') (hbb : b ≤ b') (n : ℕ) :
    response a b n ≤ response a' b' n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [response_succ, response_succ]
    exact add_le_add
      (mul_le_mul haa ih (response_nonneg a b ha hb n) (ha.trans haa))
      (pow_le_pow_left₀ hb hbb n)

theorem response_nonexpansive (a b : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b)
    (ha1 : a ≤ 1) (hb1 : b ≤ 1) (n : ℕ) : response a b n ≤ n := by
  simpa using response_mono a b 1 1 ha hb ha1 hb1 n

/-- True dynamics nonexpansive and reduced dynamics contractive give a uniform budget. -/
theorem response_uniform (a b : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b)
    (ha1 : a ≤ 1) (hb1 : b < 1) (n : ℕ) :
    response a b n ≤ 1 / (1 - b) := by
  have hd : 0 < 1 - b := sub_pos.mpr hb1
  induction n with
  | zero => exact le_of_lt (one_div_pos.mpr hd)
  | succ n ih =>
    rw [response_succ_right]
    calc
      b * response a b n + a ^ n ≤ b * (1 / (1 - b)) + 1 :=
        add_le_add (mul_le_mul_of_nonneg_left ih hb) (pow_le_one₀ ha ha1)
      _ = 1 / (1 - b) := by field_simp; ring

/-- Uniform estimates can instead use contraction on the true side. -/
theorem response_uniform_left (a b : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b)
    (ha1 : a < 1) (hb1 : b ≤ 1) (n : ℕ) :
    response a b n ≤ 1 / (1 - a) := by
  rw [response_swap]
  exact response_uniform b a hb ha hb1 ha1 n

@[simp] theorem gain_const (a : ℝ) (w : List I) : gain (fun _ : I => a) w = a ^ w.length := by
  induction w with
  | nil => simp [gain]
  | cons i w ih => simp [gain, ih, pow_succ]

@[simp] theorem budget_const (a b ε : ℝ) (w : List I) :
    budget (fun _ : I => a) (fun _ : I => b) (fun _ : I => ε) w =
      ε * response a b w.length := by
  induction w with
  | nil => simp [budget]
  | cons i w ih =>
    simp only [budget, gain_const, ih, List.length_cons, response_succ]
    ring

end Komorebi.SufficientResolution.ScalarBudgets
