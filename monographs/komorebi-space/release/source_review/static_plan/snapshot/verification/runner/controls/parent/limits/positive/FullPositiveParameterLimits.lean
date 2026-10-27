import KomorebiSpace.RegularizationLimits

set_option autoImplicit false
noncomputable section
open Filter
open scoped Topology
open KomorebiSpace

-- The result applies to every positive parameter approaching zero, and survives
-- composition with an arbitrary filter; no selected sequence is substituted.
example {H Y I : Type*}
    [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
    [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
    (T : H →L[ℝ] Y) (r : Y) (l : Filter I) (α : I → ℝ)
    (hα : Tendsto α l (𝓝[>] (0 : ℝ))) :
    Tendsto (fun i => T (RegularizationLimits.path T r (α i))) l
      (𝓝 (BudgetProfile.projectedDatum T r)) ∧
    Tendsto (fun i => ‖r - T (RegularizationLimits.path T r (α i))‖) l
      (𝓝 ‖r - BudgetProfile.projectedDatum T r‖) ∧
    Tendsto (fun i => α i * ‖RegularizationLimits.path T r (α i)‖ ^ 2) l (𝓝 0) := by
  exact ⟨(RegularizationLimits.fitted_tendsto_projectedDatum T r).comp hα,
    (RegularizationLimits.residual_norm_tendsto_floor T r).comp hα,
    (RegularizationLimits.weighted_penalty_tendsto_zero T r).comp hα⟩

-- A nonzero residual floor is permitted. For the zero operator and datum 3,
-- all fitted images are zero and the limiting residual norm is exactly 3.
example :
    Tendsto (fun α : ℝ => ‖(3 : ℝ) - (0 : ℝ →L[ℝ] ℝ)
      (RegularizationLimits.path (0 : ℝ →L[ℝ] ℝ) 3 α)‖) (𝓝[>] 0) (𝓝 3) := by
  have hp : BudgetProfile.projectedDatum (0 : ℝ →L[ℝ] ℝ) 3 = 0 := by
    simp [BudgetProfile.projectedDatum, BudgetProfile.rangeClosure]
  convert RegularizationLimits.residual_norm_tendsto_floor (0 : ℝ →L[ℝ] ℝ) 3 using 1
  rw [hp]
  norm_num

example : Tendsto (fun α : ℝ => α *
    ‖RegularizationLimits.path (0 : ℝ →L[ℝ] ℝ) 3 α‖ ^ 2) (𝓝[>] 0) (𝓝 0) := by
  exact RegularizationLimits.weighted_penalty_tendsto_zero _ _
