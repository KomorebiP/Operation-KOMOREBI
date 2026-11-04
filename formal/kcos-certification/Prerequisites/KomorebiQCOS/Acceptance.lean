import KomorebiQCOS.Certificates
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

/-!
# Multiplicative accuracy and an exact rational acceptance checker

The checker verifies the final acceptance inequality on exact rational endpoints.
It does not manufacture or verify the analytic enclosure itself. The real-valued
soundness theorem states that remaining input obligation explicitly.
-/

namespace KomorebiQCOS

/-- The division-free form of the public multiplicative accuracy contract. -/
def MultiplicativeBudget (lower upper tolerance : ℝ) : Prop :=
  0 < lower ∧ upper ≤ (1 + tolerance) * lower

theorem multiplicativeBudget_iff_ratio {lower upper tolerance : ℝ} (hl : 0 < lower) :
    MultiplicativeBudget lower upper tolerance ↔ upper / lower - 1 ≤ tolerance := by
  unfold MultiplicativeBudget
  rw [and_iff_right hl, sub_le_iff_le_add, div_le_iff₀ hl]
  rw [add_comm tolerance 1]

theorem multiplicativeBudget_tolerance_nonneg {p lower upper tolerance : ℝ}
    (hp : Enclosed p lower upper) (hb : MultiplicativeBudget lower upper tolerance) :
    0 ≤ tolerance := by
  have hprod : 0 ≤ tolerance * lower := by
    nlinarith [enclosed_order hp, hb.2]
  by_contra hn
  have hnprod := mul_neg_of_neg_of_pos (lt_of_not_ge hn) hb.1
  linarith

/-- Every point in an accepted interval has the requested relative error against
its true positive enclosed value, not merely against the lower endpoint. -/
theorem multiplicativeBudget_relative_error {p estimate lower upper tolerance : ℝ}
    (hp : Enclosed p lower upper) (he : Enclosed estimate lower upper)
    (hb : MultiplicativeBudget lower upper tolerance) :
    |estimate - p| / p ≤ tolerance := by
  have hp0 : 0 < p := hb.1.trans_le hp.1
  have ht : 0 ≤ tolerance := multiplicativeBudget_tolerance_nonneg hp hb
  have hw : upper - lower ≤ tolerance * lower := by nlinarith [hb.2]
  have hscale : tolerance * lower ≤ tolerance * p := mul_le_mul_of_nonneg_left hp.1 ht
  have habs : |estimate - p| ≤ upper - lower := by
    rw [abs_le]
    constructor <;> linarith [hp.1, hp.2, he.1, he.2]
  exact (div_le_iff₀ hp0).2 (habs.trans (hw.trans hscale))

/-- The ratio criterion implies interval order only after an enclosure is supplied.
The explicit rational checker below validates order as well. -/
theorem multiplicativeBudget_width {lower upper tolerance : ℝ}
    (hb : MultiplicativeBudget lower upper tolerance) :
    upper / lower - 1 ≤ tolerance :=
  (multiplicativeBudget_iff_ratio hb.1).1 hb

/-- An executable, exact-rational interval acceptance decision. -/
def acceptsRational (lower upper tolerance : ℚ) : Bool :=
  decide (0 < lower ∧ lower ≤ upper ∧ 0 ≤ tolerance ∧
    upper ≤ (1 + tolerance) * lower)

theorem acceptsRational_iff (lower upper tolerance : ℚ) :
    acceptsRational lower upper tolerance = true ↔
      0 < lower ∧ lower ≤ upper ∧ 0 ≤ tolerance ∧
        upper ≤ (1 + tolerance) * lower := by
  simp [acceptsRational]

theorem acceptsRational_sound {lower upper tolerance : ℚ}
    (h : acceptsRational lower upper tolerance = true) :
    MultiplicativeBudget (lower : ℝ) (upper : ℝ) (tolerance : ℝ) := by
  rcases (acceptsRational_iff lower upper tolerance).1 h with ⟨hl, _, _, hb⟩
  constructor
  · exact_mod_cast hl
  · exact_mod_cast hb

theorem acceptsRational_order {lower upper tolerance : ℚ}
    (h : acceptsRational lower upper tolerance = true) : (lower : ℝ) ≤ (upper : ℝ) := by
  exact_mod_cast ((acceptsRational_iff lower upper tolerance).1 h).2.1

/-- Soundness of the executable decision for any independently enclosed real value. -/
theorem acceptsRational_relative_error {lower upper tolerance : ℚ} {p estimate : ℝ}
    (hp : Enclosed p (lower : ℝ) (upper : ℝ))
    (he : Enclosed estimate (lower : ℝ) (upper : ℝ))
    (h : acceptsRational lower upper tolerance = true) :
    |estimate - p| / p ≤ (tolerance : ℝ) :=
  multiplicativeBudget_relative_error hp he (acceptsRational_sound h)

/-- Stronger requested tolerances cannot turn a rejection into an acceptance. -/
theorem acceptsRational_mono_tolerance {lower upper small large : ℚ}
    (h : acceptsRational lower upper small = true) (hle : small ≤ large) :
    acceptsRational lower upper large = true := by
  rcases (acceptsRational_iff lower upper small).1 h with ⟨hl, hlu, hs, hb⟩
  apply (acceptsRational_iff lower upper large).2
  refine ⟨hl, hlu, hs.trans hle, ?_⟩
  exact hb.trans (mul_le_mul_of_nonneg_right (add_le_add le_rfl hle) hl.le)

/-- Narrowing a valid positive interval preserves the same accepted tolerance. -/
theorem acceptsRational_narrow {lower upper innerLower innerUpper tolerance : ℚ}
    (h : acceptsRational lower upper tolerance = true)
    (hl : lower ≤ innerLower) (hu : innerUpper ≤ upper)
    (hi : innerLower ≤ innerUpper) :
    acceptsRational innerLower innerUpper tolerance = true := by
  rcases (acceptsRational_iff lower upper tolerance).1 h with ⟨hp, _, ht, hb⟩
  apply (acceptsRational_iff innerLower innerUpper tolerance).2
  refine ⟨hp.trans_le hl, hi, ht, ?_⟩
  have hfac : 0 ≤ 1 + tolerance := by linarith
  exact hu.trans (hb.trans (mul_le_mul_of_nonneg_left hl hfac))

/-- For a midpoint estimate, the relative point-error budget has denominator 1+τ. -/
theorem midpoint_budget_iff {estimate radius tolerance : ℝ}
    (he : radius < estimate) (ht : 0 ≤ tolerance) :
    radius / (estimate - radius) ≤ tolerance ↔
      radius ≤ tolerance * estimate / (1 + tolerance) := by
  have hden : 0 < estimate - radius := sub_pos.mpr he
  have hfac : 0 < 1 + tolerance := by linarith
  rw [div_le_iff₀ hden, le_div_iff₀ hfac]
  constructor <;> intro h <;> nlinarith

/-- For the full symmetric interval, the multiplicative width has denominator 2+ε.
This is deliberately distinct from the midpoint's relative-error budget. -/
theorem symmetric_interval_budget_iff {estimate radius tolerance : ℝ}
    (he : radius < estimate) (ht : 0 ≤ tolerance) :
    MultiplicativeBudget (estimate - radius) (estimate + radius) tolerance ↔
      radius ≤ tolerance * estimate / (2 + tolerance) := by
  have hden : 0 < estimate - radius := sub_pos.mpr he
  have hfac : 0 < 2 + tolerance := by linarith
  unfold MultiplicativeBudget
  rw [and_iff_right hden, le_div_iff₀ hfac]
  constructor <;> intro h <;> nlinarith

end KomorebiQCOS
