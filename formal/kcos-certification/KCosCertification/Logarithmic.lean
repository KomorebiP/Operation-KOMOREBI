import KomorebiQCOS.Acceptance
import Mathlib.Analysis.SpecialFunctions.Log.Basic

/-!
# Exact logarithmic consequences of a valid positive K-COS enclosure

This companion fills the positive-domain logarithm and logarithmic acceptance
obligations identified by the publication concordance. It reuses the retained
real enclosure and multiplicative-budget definitions. All endpoints below are
exact real numbers. Construction of valid numerical endpoints, parsing,
directed rounding, and correctness of the COS remainder remain hypotheses
outside this module.
-/

set_option autoImplicit false

namespace KCosCertification

open KomorebiQCOS

/-- Base-ten logarithm, used only with positive enclosed values. -/
noncomputable def decimalLog (x : ℝ) : ℝ := Real.log x / Real.log 10

/-- Positive real value corresponding to a logarithmic endpoint. -/
noncomputable def decimalExp (x : ℝ) : ℝ := Real.exp (Real.log 10 * x)

/-- Exact semantic counterpart of `expm1(log(10) * (right - left))`.
This definition does not model a numerical interval-library evaluation. -/
noncomputable def logWidthRatio (lower upper : ℝ) : ℝ :=
  Real.exp (Real.log 10 * (upper - lower)) - 1

/-- The real logarithm preserves an enclosure whose lower endpoint is positive.
Global monotonicity of Lean's totalized real logarithm is neither assumed nor true. -/
theorem enclosed_log {p lower upper : ℝ}
    (h : Enclosed p lower upper) (hl : 0 < lower) :
    Enclosed (Real.log p) (Real.log lower) (Real.log upper) := by
  exact ⟨Real.log_le_log hl h.1,
    Real.log_le_log (hl.trans_le h.1) h.2⟩

/-- Division by the positive constant `log 10` preserves endpoint order. -/
theorem enclosed_decimalLog {p lower upper : ℝ}
    (h : Enclosed p lower upper) (hl : 0 < lower) :
    Enclosed (decimalLog p) (decimalLog lower) (decimalLog upper) := by
  have hc : 0 < Real.log 10 := Real.log_pos (by norm_num)
  have hh := enclosed_log h hl
  exact ⟨div_le_div_of_nonneg_right hh.1 hc.le,
    div_le_div_of_nonneg_right hh.2 hc.le⟩

theorem decimalExp_pos (x : ℝ) : 0 < decimalExp x := Real.exp_pos _

/-- Positive values survive the logarithmic coordinate change exactly. -/
theorem decimalExp_decimalLog {p : ℝ} (hp : 0 < p) :
    decimalExp (decimalLog p) = p := by
  have hc : Real.log (10 : ℝ) ≠ 0 := ne_of_gt (Real.log_pos (by norm_num))
  unfold decimalExp decimalLog
  have h : Real.log 10 * (Real.log p / Real.log 10) = Real.log p := by
    field_simp
  rw [h, Real.exp_log hp]

/-- Logarithmic and positive-probability enclosure statements are equivalent. -/
theorem decimalLog_enclosure_iff {p lower upper : ℝ} (hp : 0 < p) :
    Enclosed (decimalLog p) lower upper ↔
      Enclosed p (decimalExp lower) (decimalExp upper) := by
  have hc : 0 < Real.log 10 := Real.log_pos (by norm_num)
  constructor
  · intro h
    have hl : Real.log 10 * lower ≤ Real.log p := by
      have hh := (le_div_iff₀ hc).1 h.1
      nlinarith
    have hu : Real.log p ≤ Real.log 10 * upper := by
      have hh := (div_le_iff₀ hc).1 h.2
      nlinarith
    constructor
    · calc
        decimalExp lower ≤ Real.exp (Real.log p) := Real.exp_le_exp.mpr hl
        _ = p := Real.exp_log hp
    · calc
        p = Real.exp (Real.log p) := (Real.exp_log hp).symm
        _ ≤ decimalExp upper := Real.exp_le_exp.mpr hu
  · intro h
    have hh := enclosed_log h (decimalExp_pos lower)
    change Real.log (decimalExp lower) ≤ Real.log p ∧
      Real.log p ≤ Real.log (decimalExp upper) at hh
    simp only [decimalExp, Real.log_exp] at hh
    constructor
    · apply (le_div_iff₀ hc).2
      nlinarith [hh.1]
    · apply (div_le_iff₀ hc).2
      nlinarith [hh.2]

/-- The logarithmic width has exactly the original multiplicative meaning. -/
theorem decimalExp_ratio (lower upper : ℝ) :
    decimalExp upper / decimalExp lower - 1 = logWidthRatio lower upper := by
  unfold decimalExp logWidthRatio
  rw [mul_sub, Real.exp_sub]

/-- The exact log-width acceptance rule is the existing multiplicative contract. -/
theorem logWidthRatio_budget_iff {lower upper tolerance : ℝ} :
    MultiplicativeBudget (decimalExp lower) (decimalExp upper) tolerance ↔
      logWidthRatio lower upper ≤ tolerance := by
  rw [multiplicativeBudget_iff_ratio (decimalExp_pos lower), decimalExp_ratio]

/-- Any point inside an accepted logarithmic enclosure has the requested relative
error against its true enclosed positive value. -/
theorem log_enclosure_relative_error {p estimate lower upper tolerance : ℝ}
    (hp : 0 < p) (he : Enclosed (decimalLog p) lower upper)
    (hx : Enclosed estimate (decimalExp lower) (decimalExp upper))
    (hb : logWidthRatio lower upper ≤ tolerance) :
    |estimate - p| / p ≤ tolerance := by
  exact multiplicativeBudget_relative_error
    ((decimalLog_enclosure_iff hp).1 he) hx (logWidthRatio_budget_iff.mpr hb)

/-- A directed upper bound for the width and a directed lower bound for the
requested tolerance suffice. Correct construction of both bounds is explicit. -/
theorem directed_log_acceptance {p estimate lower upper ratioUpper toleranceLower tolerance : ℝ}
    (hp : 0 < p) (he : Enclosed (decimalLog p) lower upper)
    (hx : Enclosed estimate (decimalExp lower) (decimalExp upper))
    (hr : logWidthRatio lower upper ≤ ratioUpper)
    (ht : toleranceLower ≤ tolerance) (ha : ratioUpper ≤ toleranceLower) :
    |estimate - p| / p ≤ tolerance :=
  log_enclosure_relative_error hp he hx (hr.trans (ha.trans ht))

/-- Valid logarithmic endpoints have a nonnegative multiplicative width. -/
theorem logWidthRatio_nonneg {lower upper : ℝ} (h : lower ≤ upper) :
    0 ≤ logWidthRatio lower upper := by
  have hc : 0 ≤ Real.log 10 := (Real.log_pos (by norm_num)).le
  have hmul : 0 ≤ Real.log 10 * (upper - lower) :=
    mul_nonneg hc (sub_nonneg.mpr h)
  have hh := Real.exp_le_exp.mpr hmul
  simpa [logWidthRatio] using sub_nonneg.mpr (show 1 ≤ Real.exp (Real.log 10 * (upper - lower)) by simpa using hh)

/-- Narrower log endpoints can only improve the exact width guarantee. -/
theorem logWidthRatio_narrow {lower upper innerLower innerUpper : ℝ}
    (hl : lower ≤ innerLower) (hu : innerUpper ≤ upper) :
    logWidthRatio innerLower innerUpper ≤ logWidthRatio lower upper := by
  have hc : 0 ≤ Real.log 10 := (Real.log_pos (by norm_num)).le
  have hw : innerUpper - innerLower ≤ upper - lower := by linarith
  exact sub_le_sub_right (Real.exp_le_exp.mpr (mul_le_mul_of_nonneg_left hw hc)) 1

/-- Narrowing valid logarithmic bounds preserves an accepted tolerance. -/
theorem logWidthRatio_narrow_accepts {lower upper innerLower innerUpper tolerance : ℝ}
    (hl : lower ≤ innerLower) (hu : innerUpper ≤ upper)
    (hb : logWidthRatio lower upper ≤ tolerance) :
    logWidthRatio innerLower innerUpper ≤ tolerance :=
  (logWidthRatio_narrow hl hu).trans hb

/-- Exact positive exponential prefactors transport the tilted-sum enclosure
into the logarithmic probability coordinates used by `interval_positive_logsf`. -/
theorem prefactor_log_enclosure {s lower upper : ℝ}
    (h : Enclosed s lower upper) (hl : 0 < lower) (c : ℝ) :
    Enclosed (decimalLog (Real.exp c * s))
      ((c + Real.log lower) / Real.log 10)
      ((c + Real.log upper) / Real.log 10) := by
  have hs : 0 < s := hl.trans_le h.1
  have hc : 0 < Real.log 10 := Real.log_pos (by norm_num)
  have hh := enclosed_log h hl
  unfold decimalLog
  rw [Real.log_mul (ne_of_gt (Real.exp_pos c)) (ne_of_gt hs), Real.log_exp]
  exact ⟨div_le_div_of_nonneg_right (add_le_add le_rfl hh.1) hc.le,
    div_le_div_of_nonneg_right (add_le_add le_rfl hh.2) hc.le⟩

/-- An independently enclosed log-prefactor contributes its own endpoint error.
This is the interval-shaped version of the backend's log transformation; it
makes no assertion that the prefactor or tilted sum bounds were computed correctly. -/
theorem prefactor_interval_log_enclosure {s lower upper c cLower cUpper : ℝ}
    (hs : Enclosed s lower upper) (hl : 0 < lower)
    (hc : Enclosed c cLower cUpper) :
    Enclosed (decimalLog (Real.exp c * s))
      ((cLower + Real.log lower) / Real.log 10)
      ((cUpper + Real.log upper) / Real.log 10) := by
  have h := prefactor_log_enclosure hs hl c
  have hd : 0 ≤ Real.log 10 := (Real.log_pos (by norm_num)).le
  exact ⟨(div_le_div_of_nonneg_right (add_le_add hc.1 le_rfl) hd).trans h.1,
    h.2.trans (div_le_div_of_nonneg_right (add_le_add hc.2 le_rfl) hd)⟩

/-- A common exact exponential prefactor cancels from the multiplicative width.
Numerical enclosure widening is not asserted to cancel. -/
theorem prefactor_log_width {lower upper : ℝ}
    (hl : 0 < lower) (hu : 0 < upper) (c : ℝ) :
    logWidthRatio (decimalLog (Real.exp c * lower))
      (decimalLog (Real.exp c * upper)) = upper / lower - 1 := by
  rw [← decimalExp_ratio,
    decimalExp_decimalLog (mul_pos (Real.exp_pos c) hu),
    decimalExp_decimalLog (mul_pos (Real.exp_pos c) hl)]
  have he : Real.exp c ≠ 0 := ne_of_gt (Real.exp_pos c)
  congr 1
  field_simp

end KCosCertification
