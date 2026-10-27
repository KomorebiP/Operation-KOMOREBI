import KomorebiSpace.RegularizationStrongLimit

set_option autoImplicit false
noncomputable section
open Filter
open scoped Topology
open KomorebiSpace

-- Range membership constructs a unique minimum norm preimage and its strong
-- limit in arbitrary real Hilbert spaces; no closed range hypothesis appears.
example {H Y : Type*}
    [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
    [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
    (T : H →L[ℝ] Y) (r : Y)
    (hb : BudgetProfile.projectedDatum T r ∈ Set.range T) :
    ∃! a : H, (T a = BudgetProfile.projectedDatum T r ∧
        ∀ x : H, T x = BudgetProfile.projectedDatum T r → ‖a‖ ≤ ‖x‖) ∧
      Tendsto (RegularizationLimits.path T r) (𝓝[>] (0 : ℝ)) (𝓝 a) := by
  exact RegularizationStrongLimit.exists_unique_minimum_and_limit T r hb

-- The positive residual floor for a zero operator coexists with a strong
-- correction limit of zero, which is the unique minimum norm preimage of 0.
example : Tendsto (RegularizationLimits.path (0 : ℝ →L[ℝ] ℝ) 3)
    (𝓝[>] (0 : ℝ)) (𝓝 (0 : ℝ)) := by
  apply RegularizationStrongLimit.path_tendsto_of_minimum
  · simp [BudgetProfile.projectedDatum, BudgetProfile.rangeClosure]
  · intro x _
    simpa only [norm_zero] using norm_nonneg x

-- The unattained case is divergence past every finite budget, not just failure
-- of convergence or existence of a single escaping sequence.
example {H Y : Type*}
    [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
    [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
    (T : H →L[ℝ] Y) (r : Y)
    (hb : BudgetProfile.projectedDatum T r ∉ Set.range T) (M : ℝ) :
    ∀ᶠ α : ℝ in 𝓝[>] 0, M ≤ ‖RegularizationLimits.path T r α‖ := by
  exact (RegularizationLimits.norm_tendsto_atTop_of_not_mem_range T r hb).eventually
    (eventually_ge_atTop M)
