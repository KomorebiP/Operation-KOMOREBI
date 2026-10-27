import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith

/-!
# Arithmetic consequences of supplied enclosures

This module proves what follows from valid exact-real error bounds. It does
not prove COS inversion, support/alias bounds, mode-tail estimates, spectral
inclusion, or the correctness of mpmath.iv.
-/

namespace KomorebiQCOS

/-- A mathematical enclosure of one exact real number. -/
def Enclosed (value lower upper : ℝ) : Prop := lower ≤ value ∧ value ≤ upper

/-- An exact-real additive error budget. -/
def ErrorBound (value estimate radius : ℝ) : Prop := |value - estimate| ≤ radius

theorem enclosed_order {value lower upper : ℝ}
    (h : Enclosed value lower upper) : lower ≤ upper :=
  h.1.trans h.2

theorem enclosed_add {x y lx ux ly uy : ℝ}
    (hx : Enclosed x lx ux) (hy : Enclosed y ly uy) :
    Enclosed (x + y) (lx + ly) (ux + uy) := by
  exact ⟨add_le_add hx.1 hy.1, add_le_add hx.2 hy.2⟩

theorem enclosed_scale {value lower upper a : ℝ}
    (ha : 0 ≤ a) (h : Enclosed value lower upper) :
    Enclosed (a * value) (a * lower) (a * upper) := by
  exact ⟨mul_le_mul_of_nonneg_left h.1 ha, mul_le_mul_of_nonneg_left h.2 ha⟩

theorem enclosed_widen {value lower upper lo hi : ℝ}
    (h : Enclosed value lower upper) (hl : lo ≤ lower) (hu : upper ≤ hi) :
    Enclosed value lo hi :=
  ⟨hl.trans h.1, h.2.trans hu⟩

/-- Multiple independently valid enclosures may be intersected. -/
theorem enclosed_intersect {value l₁ u₁ l₂ u₂ : ℝ}
    (h₁ : Enclosed value l₁ u₁) (h₂ : Enclosed value l₂ u₂) :
    Enclosed value (max l₁ l₂) (min u₁ u₂) := by
  exact ⟨max_le h₁.1 h₂.1, le_min h₁.2 h₂.2⟩

theorem errorBound_iff_enclosed (value estimate radius : ℝ) :
    ErrorBound value estimate radius ↔
      Enclosed value (estimate - radius) (estimate + radius) := by
  unfold ErrorBound Enclosed
  rw [abs_le]
  constructor
  · rintro ⟨hl, hu⟩
    constructor <;> linarith
  · rintro ⟨hl, hu⟩
    constructor <;> linarith

/-- Error bounds from arithmetic and analysis combine additively. -/
theorem errorBound_compose {value middle estimate analytic arithmetic : ℝ}
    (ha : ErrorBound value middle analytic)
    (hr : ErrorBound middle estimate arithmetic) :
    ErrorBound value estimate (analytic + arithmetic) := by
  unfold ErrorBound at *
  calc
    |value - estimate| = |(value - middle) + (middle - estimate)| := by
      congr 1
      linarith
    _ ≤ |value - middle| + |middle - estimate| := abs_add_le _ _
    _ ≤ analytic + arithmetic := add_le_add ha hr

/-- Once the sum of all proved error budgets is within tolerance, the output
has the corresponding exact-real absolute error guarantee. -/
theorem errorBound_accept {value middle estimate analytic arithmetic tolerance : ℝ}
    (ha : ErrorBound value middle analytic)
    (hr : ErrorBound middle estimate arithmetic)
    (hbudget : analytic + arithmetic ≤ tolerance) :
    ErrorBound value estimate tolerance :=
  (errorBound_compose ha hr).trans hbudget

/-- A strictly positive lower interval endpoint proves positivity. -/
theorem enclosed_positive {value lower upper : ℝ}
    (h : Enclosed value lower upper) (hl : 0 < lower) : 0 < value :=
  hl.trans_le h.1

/-- Monotone transformations carry an enclosure to their endpoint images.
The transformation's monotonicity is an explicit hypothesis. -/
theorem enclosed_monotone {f : ℝ → ℝ} (hf : Monotone f)
    {value lower upper : ℝ} (h : Enclosed value lower upper) :
    Enclosed (f value) (f lower) (f upper) :=
  ⟨hf h.1, hf h.2⟩

end KomorebiQCOS
