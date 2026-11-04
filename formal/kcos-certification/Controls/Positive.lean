import KCosCertification

set_option autoImplicit false
open KCosCertification KomorebiQCOS

namespace KCosCertification.Controls

-- A one-decade interval has a ratio excess of nine, not one.
theorem oneDecadeRatio : logWidthRatio 0 1 = 9 := by
  norm_num [logWidthRatio, Real.exp_log (by norm_num : (0 : ℝ) < 10)]

theorem zeroWidth (x : ℝ) : logWidthRatio x x = 0 := by
  simp [logWidthRatio]

theorem positiveLogEnclosure : Enclosed (Real.log 3) (Real.log 2) (Real.log 5) := by
  apply enclosed_log
  · constructor <;> norm_num
  · norm_num

-- Positivity is a mathematical boundary: Lean's totalized log is not
-- order preserving on every nonnegative interval.
theorem nonpositiveLogCounterexample : ¬ Enclosed (Real.log 0) (Real.log 0) (Real.log (1 / 2 : ℝ)) := by
  intro h
  have hn : Real.log (1 / 2 : ℝ) < 0 := Real.log_neg (by norm_num) (by norm_num)
  have hh := h.2
  simp only [Real.log_zero] at hh
  linarith

-- Exercise the logarithmic acceptance bridge on exact positive endpoints.
theorem concreteAcceptedEstimate : |(3 : ℝ) - 2| / 2 ≤ 1 := by
  apply log_enclosure_relative_error (lower := decimalLog 2) (upper := decimalLog 3)
  · norm_num
  · apply enclosed_decimalLog
    · constructor <;> norm_num
    · norm_num
  · rw [decimalExp_decimalLog (by norm_num : (0 : ℝ) < 2),
        decimalExp_decimalLog (by norm_num : (0 : ℝ) < 3)]
    constructor <;> norm_num
  · have h := prefactor_log_width (by norm_num : (0 : ℝ) < 2)
        (by norm_num : (0 : ℝ) < 3) 0
    simp only [Real.exp_zero, one_mul] at h
    rw [h]
    norm_num

-- A directed enclosure whose upper width is accepted implies the real
-- tolerance bound when the tolerance itself was rounded down.
theorem directedTolerance {p estimate lower upper ratioUpper : ℝ}
    (hp : 0 < p) (he : Enclosed (decimalLog p) lower upper)
    (hx : Enclosed estimate (decimalExp lower) (decimalExp upper))
    (hr : logWidthRatio lower upper ≤ ratioUpper)
    (ha : ratioUpper ≤ (1 / 100 : ℝ)) :
    |estimate - p| / p ≤ (11 / 1000 : ℝ) := by
  exact directed_log_acceptance hp he hx hr (by norm_num) ha

-- A degenerate refinement preserves the outer accepted bound.
theorem narrowingPreservesBudget : logWidthRatio 0 0 ≤ 9 := by
  apply logWidthRatio_narrow_accepts (lower := 0) (upper := 1)
  · norm_num
  · norm_num
  · norm_num [logWidthRatio, Real.exp_log (by norm_num : (0 : ℝ) < 10)]

-- The log-prefactor itself may have an independent enclosure.
theorem enclosedPrefactor : Enclosed (decimalLog (Real.exp 2 * 3))
    ((1 + Real.log 2) / Real.log 10) ((3 + Real.log 4) / Real.log 10) := by
  apply prefactor_interval_log_enclosure
  · constructor <;> norm_num
  · norm_num
  · constructor <;> norm_num

end KCosCertification.Controls
