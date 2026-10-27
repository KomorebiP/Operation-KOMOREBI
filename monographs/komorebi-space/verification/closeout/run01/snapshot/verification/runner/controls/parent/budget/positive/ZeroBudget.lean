import KomorebiSpace.BudgetProfileGeometry
import KomorebiSpace.BudgetDuality

set_option autoImplicit false
noncomputable section
open scoped RealInnerProductSpace
open KomorebiSpace

variable {H Y : Type*}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]

example (T : H →L[ℝ] Y) (r : Y) : BudgetProfile.beta T r 0 = ‖r‖ :=
  BudgetProfileGeometry.beta_zero T r

example (T : H →L[ℝ] Y) (r : Y) :
    0 ≤ BudgetProfile.beta T r 0 - BudgetProfile.beta T r 0 ∧
      BudgetProfile.beta T r 0 - BudgetProfile.beta T r 0 ≤ ‖T‖ * (0 - 0) :=
  BudgetProfileGeometry.beta_profile_bounds T r (le_refl 0) (le_refl 0)

example (T : H →L[ℝ] Y) (r : Y) : ∃ z : Y, ‖z‖ ≤ 1 ∧
    ⟪r, z⟫ = ‖r‖ := by
  obtain ⟨z, hz, heq⟩ := BudgetDuality.exists_attaining_dual_witness T r (le_refl 0)
  refine ⟨z, hz, ?_⟩
  simpa only [zero_mul, sub_zero, BudgetProfileGeometry.beta_zero] using heq

example (T : H →L[ℝ] Y) {M : ℝ} (hM : 0 ≤ M) :
    ∃ z : Y, ‖z‖ ≤ 1 ∧ ⟪(0 : Y), z⟫ - M * ‖T.adjoint z‖ = 0 := by
  have hb : BudgetProfile.beta T 0 M = 0 := by
    apply le_antisymm _ (BudgetProfile.beta_nonneg _ _ _)
    simpa using BudgetProfile.beta_le_residual T (0 : Y) (a := 0) (by simpa using hM)
  simpa only [hb] using BudgetDuality.exists_attaining_dual_witness T (0 : Y) hM
