import Mathlib.Tactic.Ring
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Basic.Real.Basic

set_option autoImplicit false

namespace KomorebiAddMul.Block03

/-- Arbitrary finite annihilating filters give a certified worst-case
reconstruction cost, independently of how the correction was constructed. -/
theorem finite_filter_error_budget
    {n : ℕ} (w e : Fin n → ℝ) (M : ℝ)
    (he : ∀ i, |e i| ≤ M) :
    |∑ i : Fin n, w i * e i| ≤ (∑ i : Fin n, |w i|) * M := by
  calc
    |∑ i : Fin n, w i * e i|
      ≤ ∑ i : Fin n, |w i * e i| := Finset.abs_sum_le_sum_abs _ _
    _ = ∑ i : Fin n, |w i| * |e i| := by simp only [abs_mul]
    _ ≤ ∑ i : Fin n, |w i| * M := by
      apply Finset.sum_le_sum
      intro i hi
      exact mul_le_mul_of_nonneg_left (he i) (abs_nonneg (w i))
    _ = (∑ i : Fin n, |w i|) * M := by rw [Finset.sum_mul]

/-- If a filter annihilates the admissible correction, the same finite
certificate lower-bounds the approximation error on target observations. -/
theorem protected_filter_error_budget
    {n : ℕ} (w target correction : Fin n → ℝ) (M : ℝ)
    (hkill : ∑ i : Fin n, w i * correction i = 0)
    (herr : ∀ i, |target i - correction i| ≤ M) :
    |∑ i : Fin n, w i * target i| ≤ (∑ i : Fin n, |w i|) * M := by
  have h := finite_filter_error_budget w (fun i => target i - correction i) M herr
  have hs : (∑ i : Fin n, w i * (target i - correction i)) =
      (∑ i : Fin n, w i * target i) - (∑ i : Fin n, w i * correction i) := by
    simp only [mul_sub, Finset.sum_sub_distrib]
  rw [hs,hkill,sub_zero] at h
  exact h

end KomorebiAddMul.Block03

-- Verification/Axiom audit (part of reproducible source).
#print axioms KomorebiAddMul.Block03.finite_filter_error_budget
#print axioms KomorebiAddMul.Block03.protected_filter_error_budget
