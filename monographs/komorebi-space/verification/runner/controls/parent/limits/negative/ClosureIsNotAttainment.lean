import KomorebiSpace.RegularizationStrongLimit

set_option autoImplicit false
noncomputable section
open Filter
open scoped Topology
open KomorebiSpace

-- Deliberately invalid replacement of actual range membership by closure
-- membership, which holds automatically and cannot imply a minimum preimage.
example {H Y : Type*}
    [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
    [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
    (T : H →L[ℝ] Y) (r : Y)
    (hclosure : BudgetProfile.projectedDatum T r ∈ closure (Set.range T)) :
    ∃! a : H, (T a = BudgetProfile.projectedDatum T r ∧
        ∀ x : H, T x = BudgetProfile.projectedDatum T r → ‖a‖ ≤ ‖x‖) ∧
      Tendsto (RegularizationLimits.path T r) (𝓝[>] (0 : ℝ)) (𝓝 a) := by
  exact RegularizationStrongLimit.exists_unique_minimum_and_limit T r hclosure
