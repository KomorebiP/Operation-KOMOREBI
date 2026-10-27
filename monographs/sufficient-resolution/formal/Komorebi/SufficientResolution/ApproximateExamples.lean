import Komorebi.SufficientResolution.ApproximateComposition
import Mathlib.Algebra.Order.Archimedean.Basic

/-!
# Sharpness and a universal counterexample to growth-free approximation claims

These are exact real scalar systems, not floating-point experiments. The scalar
convolution bound is attained. Arbitrarily small positive one-step error can grow
past every bound when growth control is absent.
-/

set_option autoImplicit false

namespace Komorebi.SufficientResolution.ApproximateExamples

open ApproximateBounds ScalarBudgets

/-- Multiplication by a real scalar as a continuous linear map. -/
def scalar (a : ℝ) : ℝ →L[ℝ] ℝ := a • ContinuousLinearMap.id ℝ ℝ

@[simp] theorem scalar_apply (a x : ℝ) : scalar a x = a * x := rfl

@[simp] theorem norm_scalar (a : ℝ) : ‖scalar a‖ = |a| := by
  simp [scalar, norm_smul, Real.norm_eq_abs]

@[simp] theorem scalar_one : scalar 1 = ContinuousLinearMap.id ℝ ℝ := by
  simp [scalar]

theorem scalar_word (a : ℝ) (w : List Unit) :
    word (fun _ : Unit => scalar a) w = scalar (a ^ w.length) := by
  induction w with
  | nil => simp
  | cons i w ih =>
    apply ContinuousLinearMap.ext
    intro x
    simp [word_cons, ih, pow_succ, mul_assoc]

theorem scalar_stepError (a b : ℝ) :
    stepError (scalar 1) (fun _ : Unit => scalar a) (fun _ : Unit => scalar b) () =
      scalar (a - b) := by
  apply ContinuousLinearMap.ext
  intro x
  simp [stepError, sub_mul]

theorem scalar_wordError (a b : ℝ) (w : List Unit) :
    wordError (scalar 1) (fun _ : Unit => scalar a) (fun _ : Unit => scalar b) w =
      scalar (a ^ w.length - b ^ w.length) := by
  apply ContinuousLinearMap.ext
  intro x
  simp [wordError, scalar_word, sub_mul]

/-- The analytic estimate is an equality for these scalar systems. -/
theorem sharp_response (a b : ℝ) (hb : 0 ≤ b) (hba : b ≤ a) (w : List Unit) :
    ‖wordError (scalar 1) (fun _ : Unit => scalar a) (fun _ : Unit => scalar b) w‖ =
      (a - b) * response a b w.length := by
  rw [scalar_wordError, norm_scalar, response_mul_sub]
  exact abs_of_nonneg (sub_nonneg.mpr (pow_le_pow_left₀ hb hba w.length))

/-- Elementary growth lower bound, proved for every real epsilon >= 0 and every n. -/
theorem bernoulli_lower (ε : ℝ) (he : 0 ≤ ε) (n : ℕ) :
    1 + (n : ℝ) * ε ≤ (1 + ε) ^ n := by
  induction n with
  | zero => simp
  | succ n ih =>
    calc
      1 + (n + 1 : ℕ) * ε ≤ (1 + (n : ℝ) * ε) * (1 + ε) := by
        push_cast
        nlinarith [mul_nonneg (mul_nonneg (Nat.cast_nonneg n) he) he]
      _ ≤ (1 + ε) ^ n * (1 + ε) := mul_le_mul_of_nonneg_right ih (by linarith)
      _ = (1 + ε) ^ (n + 1) := (pow_succ _ _).symm

theorem unstable_step_exact (ε : ℝ) (he : 0 ≤ ε) :
    ‖stepError (scalar 1) (fun _ : Unit => scalar (1 + ε))
      (fun _ : Unit => scalar 1) ()‖ = ε := by
  rw [scalar_stepError, norm_scalar]
  have h : 1 + ε - 1 = ε := by ring
  rw [h, abs_of_nonneg he]

theorem unstable_word_lower (ε : ℝ) (he : 0 ≤ ε) (n : ℕ) :
    (n : ℝ) * ε ≤ ‖wordError (scalar 1) (fun _ : Unit => scalar (1 + ε))
      (fun _ : Unit => scalar 1) (List.replicate n ())‖ := by
  rw [scalar_wordError, norm_scalar]
  simp only [List.length_replicate, one_pow]
  have hp := bernoulli_lower ε he n
  have hn : 0 ≤ (1 + ε) ^ n - 1 := by
    nlinarith [mul_nonneg (Nat.cast_nonneg n) he]
  rw [abs_of_nonneg hn]
  linarith

/-- No horizon-independent error bound follows from small one-step error alone. -/
theorem unstable_error_unbounded (ε : ℝ) (he : 0 < ε) (B : ℝ) :
    ∃ n : ℕ, B < ‖wordError (scalar 1) (fun _ : Unit => scalar (1 + ε))
      (fun _ : Unit => scalar 1) (List.replicate n ())‖ := by
  obtain ⟨n, hn⟩ := exists_nat_gt (B / ε)
  have hmul : B < (n : ℝ) * ε := (div_lt_iff₀ he).mp hn
  exact ⟨n, hmul.trans_le (unstable_word_lower ε he.le n)⟩

/-- A stable sharp case exhibits the exact saturation factor 1-b^n. -/
theorem stable_scalar_exact (b : ℝ) (hb : 0 ≤ b) (hb1 : b ≤ 1) (w : List Unit) :
    ‖wordError (scalar 1) (fun _ : Unit => scalar 1) (fun _ : Unit => scalar b) w‖ =
      1 - b ^ w.length := by
  rw [scalar_wordError, norm_scalar, one_pow]
  exact abs_of_nonneg (sub_nonneg.mpr (pow_le_one₀ hb hb1))

end Komorebi.SufficientResolution.ApproximateExamples
