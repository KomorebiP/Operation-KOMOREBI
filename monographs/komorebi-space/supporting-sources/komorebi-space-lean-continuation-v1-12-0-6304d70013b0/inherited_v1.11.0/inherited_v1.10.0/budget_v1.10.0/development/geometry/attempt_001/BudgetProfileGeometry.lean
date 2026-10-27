import KomorebiSpace.BudgetProfile

/-!
# Shape of the attained budget profile (WR03)

These statements use the actual norm on the correction space. They require no
finite-dimensionality, injectivity, or closed-range assumption. The zero-budget
case is included explicitly in the profile estimate.
-/

noncomputable section

namespace KomorebiSpace.BudgetProfileGeometry

open KomorebiSpace.BudgetProfile

variable {H Y : Type*}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]

/-- Increasing a nonnegative correction budget cannot increase the best residual. -/
theorem beta_antitone (T : H →L[ℝ] Y) (r : Y) {M₁ M₂ : ℝ}
    (h₁ : 0 ≤ M₁) (h₁₂ : M₁ ≤ M₂) : beta T r M₂ ≤ beta T r M₁ := by
  obtain ⟨a, ha, hopt⟩ := exists_budget_minimizer T r h₁
  exact (beta_le_residual T r (ha.trans h₁₂)).trans_eq hopt

/-- The zero ball contains only zero, so the initial budget profile is the data norm. -/
theorem beta_zero (T : H →L[ℝ] Y) (r : Y) : beta T r 0 = ‖r‖ := by
  obtain ⟨a, ha, hopt⟩ := exists_budget_minimizer T r (le_refl 0)
  have hz : a = 0 := norm_eq_zero.mp (le_antisymm ha (norm_nonneg a))
  simpa only [hz, map_zero, sub_zero] using hopt.symm

/-- The exact convexity inequality, including both endpoints and zero budgets. -/
theorem beta_convex_combination (T : H →L[ℝ] Y) (r : Y) {M₁ M₂ t : ℝ}
    (h₁ : 0 ≤ M₁) (h₂ : 0 ≤ M₂) (ht : 0 ≤ t) (ht₁ : t ≤ 1) :
    beta T r (t * M₁ + (1 - t) * M₂) ≤
      t * beta T r M₁ + (1 - t) * beta T r M₂ := by
  obtain ⟨a₁, ha₁, heq₁⟩ := exists_budget_minimizer T r h₁
  obtain ⟨a₂, ha₂, heq₂⟩ := exists_budget_minimizer T r h₂
  have hs : 0 ≤ 1 - t := sub_nonneg.mpr ht₁
  have hfeas : ‖t • a₁ + (1 - t) • a₂‖ ≤ t * M₁ + (1 - t) * M₂ := by
    calc
      _ ≤ ‖t • a₁‖ + ‖(1 - t) • a₂‖ := norm_add_le _ _
      _ = t * ‖a₁‖ + (1 - t) * ‖a₂‖ := by
        simp only [norm_smul, Real.norm_eq_abs, abs_of_nonneg ht, abs_of_nonneg hs]
      _ ≤ _ := add_le_add (mul_le_mul_of_nonneg_left ha₁ ht)
        (mul_le_mul_of_nonneg_left ha₂ hs)
  calc
    _ ≤ ‖r - T (t • a₁ + (1 - t) • a₂)‖ := beta_le_residual T r hfeas
    _ = ‖t • (r - T a₁) + (1 - t) • (r - T a₂)‖ := by
      congr 1
      simp only [map_add, map_smul]
      module
    _ ≤ ‖t • (r - T a₁)‖ + ‖(1 - t) • (r - T a₂)‖ := norm_add_le _ _
    _ = _ := by
      simp only [norm_smul, Real.norm_eq_abs, abs_of_nonneg ht, abs_of_nonneg hs,
        heq₁, heq₂]

/-- Radially shrink any feasible vector from a positive budget to a smaller one. -/
theorem radial_shrink_bounds {a : H} {M₁ M₂ : ℝ}
    (h₁ : 0 ≤ M₁) (h₂ : 0 < M₂) (h₁₂ : M₁ ≤ M₂) (ha : ‖a‖ ≤ M₂) :
    ‖(M₁ / M₂) • a‖ ≤ M₁ ∧ ‖a - (M₁ / M₂) • a‖ ≤ M₂ - M₁ := by
  have ht : 0 ≤ M₁ / M₂ := div_nonneg h₁ h₂.le
  have ht₁ : M₁ / M₂ ≤ 1 := (div_le_one h₂).mpr h₁₂
  have hprod : (M₁ / M₂) * M₂ = M₁ := div_mul_cancel₀ M₁ (ne_of_gt h₂)
  constructor
  · calc
      _ = (M₁ / M₂) * ‖a‖ := by
        simp only [norm_smul, Real.norm_eq_abs, abs_of_nonneg ht]
      _ ≤ (M₁ / M₂) * M₂ := mul_le_mul_of_nonneg_left ha ht
      _ = M₁ := hprod
  · have heq : a - (M₁ / M₂) • a = (1 - M₁ / M₂) • a := by module
    calc
      _ = (1 - M₁ / M₂) * ‖a‖ := by
        rw [heq, norm_smul, Real.norm_eq_abs, abs_of_nonneg (sub_nonneg.mpr ht₁)]
      _ ≤ (1 - M₁ / M₂) * M₂ :=
        mul_le_mul_of_nonneg_left ha (sub_nonneg.mpr ht₁)
      _ = M₂ - M₁ := by nlinarith

/-- The one-sided Lipschitz estimate handles the degenerate upper budget explicitly. -/
theorem beta_sub_le (T : H →L[ℝ] Y) (r : Y) {M₁ M₂ : ℝ}
    (h₁ : 0 ≤ M₁) (h₁₂ : M₁ ≤ M₂) :
    beta T r M₁ - beta T r M₂ ≤ ‖T‖ * (M₂ - M₁) := by
  have h₂ : 0 ≤ M₂ := h₁.trans h₁₂
  obtain hzero | hpos := h₂.eq_or_lt
  · have hM₁ : M₁ = 0 := le_antisymm (h₁₂.trans_eq hzero.symm) h₁
    simp only [hM₁, ← hzero, sub_self, mul_zero, le_refl]
  · obtain ⟨a, ha, hopt⟩ := exists_budget_minimizer T r h₂
    obtain ⟨hb, hdiff⟩ := radial_shrink_bounds h₁ hpos h₁₂ ha
    have hbound : beta T r M₁ ≤ beta T r M₂ + ‖T‖ * (M₂ - M₁) := by
      calc
        _ ≤ ‖r - T ((M₁ / M₂) • a)‖ := beta_le_residual T r hb
        _ = ‖(r - T a) + T (a - (M₁ / M₂) • a)‖ := by
          congr 1
          simp only [map_sub]
          abel
        _ ≤ ‖r - T a‖ + ‖T (a - (M₁ / M₂) • a)‖ := norm_add_le _ _
        _ ≤ beta T r M₂ + ‖T‖ * ‖a - (M₁ / M₂) • a‖ := by
          rw [hopt]
          exact add_le_add_left (T.le_opNorm _) _
        _ ≤ _ := add_le_add_left (mul_le_mul_of_nonneg_left hdiff (norm_nonneg T)) _
    linarith

/-- Both sides of the printed WR03 profile estimate, for every ordered nonnegative pair. -/
theorem beta_profile_bounds (T : H →L[ℝ] Y) (r : Y) {M₁ M₂ : ℝ}
    (h₁ : 0 ≤ M₁) (h₁₂ : M₁ ≤ M₂) :
    0 ≤ beta T r M₁ - beta T r M₂ ∧
      beta T r M₁ - beta T r M₂ ≤ ‖T‖ * (M₂ - M₁) :=
  ⟨sub_nonneg.mpr (beta_antitone T r h₁ h₁₂), beta_sub_le T r h₁ h₁₂⟩

end KomorebiSpace.BudgetProfileGeometry
