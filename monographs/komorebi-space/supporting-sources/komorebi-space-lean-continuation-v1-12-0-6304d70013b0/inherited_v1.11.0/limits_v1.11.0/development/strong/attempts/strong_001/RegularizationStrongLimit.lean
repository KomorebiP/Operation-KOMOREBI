import KomorebiSpace.RegularizedHilbertRepair
import KomorebiSpace.BudgetProfile
import KomorebiSpace.NestedMinimumCorrections

/-!
# Strong regularization limit at an attainable projected datum (WR08)

The minimum norm preimage is constructed from the closed convex fiber. A
frequently bounded version of WR01 supplies the lower norm limit; the exact
regularized energy identity then upgrades norm convergence to strong convergence.
-/

noncomputable section

open Filter Set Topology

namespace KomorebiSpace.RegularizationStrongLimit

variable {H Y : Type*}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]

/-- A nonempty operator fiber has a unique minimum norm element, even when the
operator range is not closed. -/
theorem exists_unique_minimum_preimage (T : H →L[ℝ] Y) (b : Y)
    (hb : b ∈ Set.range T) :
    ∃! a : H, T a = b ∧ ∀ x : H, T x = b → ‖a‖ ≤ ‖x‖ := by
  have hne : (T ⁻¹' {b}).Nonempty := by
    obtain ⟨x, hx⟩ := hb
    exact ⟨x, hx⟩
  have hc : IsClosed (T ⁻¹' {b}) := isClosed_singleton.preimage T.continuous
  have hcv : Convex ℝ (T ⁻¹' {b}) := (convex_singleton b).linear_preimage T.toLinearMap
  obtain ⟨a, ha⟩ := NestedMinimumCorrections.exists_minimum (T ⁻¹' {b}) hne hc hcv
  refine ⟨a, ha, ?_⟩
  intro x hx
  exact NestedMinimumCorrections.minimum_unique hcv hx ha

/-- The least norm compatible datum forces a lower norm limit for every
approximating filter, without selecting a weakly convergent subsequence. -/
theorem norm_tendsto_of_minimum (T : H →L[ℝ] Y) (b : Y) (a : H)
    (hmin : ∀ x : H, T x = b → ‖a‖ ≤ ‖x‖)
    {ι : Type*} {l : Filter ι} [NeBot l] (u : ι → H)
    (himage : Tendsto (fun i => T (u i)) l (𝓝 b))
    (hbound : ∀ᶠ i in l, ‖u i‖ ≤ ‖a‖) :
    Tendsto (fun i => ‖u i‖) l (𝓝 ‖a‖) := by
  apply tendsto_order.mpr
  constructor
  · intro c hc
    by_contra h
    have hfreq : ∃ᶠ i in l, ‖u i‖ ≤ c := by
      simpa only [not_lt] using Filter.not_eventually.mp h
    obtain ⟨x, hx, hxc⟩ :=
      BoundedApproximateRealization.exists_solution_of_frequently_bounded T u b c hfreq himage
    exact (not_le_of_gt hc) ((hmin x hx).trans hxc)
  · intro c hc
    exact hbound.mono fun i hi => hi.trans_lt hc

/-- Exact energy comparison bounds correction distance by the difference of
norm energies at any preimage of the projected datum. -/
theorem correction_distance_sq_le (T : H →L[ℝ] Y) (r : Y) {α : ℝ}
    (hα : 0 < α) (a : H) (ha : T a = BudgetProfile.projectedDatum T r) :
    ‖RegularizedHilbertRepair.correction T α hα r - a‖ ^ 2 ≤
      ‖a‖ ^ 2 - ‖RegularizedHilbertRepair.correction T α hα r‖ ^ 2 := by
  have he := RegularizedHilbertRepair.energy_identity T α hα r a
  have hr := BudgetProfile.residual_sq_decomposition T r
    (RegularizedHilbertRepair.correction T α hα r)
  unfold RegularizedHilbertRepair.objective at he
  rw [ha, norm_sub_rev (BudgetProfile.projectedDatum T r) r,
    norm_sub_rev (T (RegularizedHilbertRepair.correction T α hα r)) r,
    norm_sub_rev a (RegularizedHilbertRepair.correction T α hα r)] at he
  nlinarith [sq_nonneg ‖T (a - RegularizedHilbertRepair.correction T α hα r)‖,
    sq_nonneg ‖BudgetProfile.projectedDatum T r -
      T (RegularizedHilbertRepair.correction T α hα r)‖]

/-- The regularized correction stays within every exact projected-data budget. -/
theorem correction_norm_le (T : H →L[ℝ] Y) (r : Y) {α : ℝ}
    (hα : 0 < α) (a : H) (ha : T a = BudgetProfile.projectedDatum T r) :
    ‖RegularizedHilbertRepair.correction T α hα r‖ ≤ ‖a‖ := by
  have he := correction_distance_sq_le T r hα a ha
  nlinarith [sq_nonneg ‖RegularizedHilbertRepair.correction T α hα r - a‖,
    norm_nonneg (RegularizedHilbertRepair.correction T α hα r), norm_nonneg a]

end KomorebiSpace.RegularizationStrongLimit
