import KomorebiSpace.RegularizationLimits
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

omit [CompleteSpace Y] in
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

omit [InnerProductSpace ℝ H] [CompleteSpace H] in
/-- An energy bound turns convergence of norms into convergence of vectors. -/
theorem tendsto_of_norm_energy_le {ι : Type*} {l : Filter ι} (u : ι → H) (a : H)
    (hnorm : Tendsto (fun i => ‖u i‖) l (𝓝 ‖a‖))
    (henergy : ∀ᶠ i in l, ‖u i - a‖ ^ 2 ≤ ‖a‖ ^ 2 - ‖u i‖ ^ 2) :
    Tendsto u l (𝓝 a) := by
  have he : Tendsto (fun i => ‖a‖ ^ 2 - ‖u i‖ ^ 2) l (𝓝 0) := by
    simpa using (tendsto_const_nhds :
      Tendsto (fun _ : ι => ‖a‖ ^ 2) l (𝓝 (‖a‖ ^ 2))).sub (hnorm.pow 2)
  apply Metric.tendsto_nhds.mpr
  intro ε hε
  have hb : ∀ᶠ i in l, ‖a‖ ^ 2 - ‖u i‖ ^ 2 < ε ^ 2 :=
    he.eventually (gt_mem_nhds (sq_pos_of_pos hε))
  filter_upwards [henergy, hb] with i hi hib
  rw [dist_eq_norm]
  nlinarith [norm_nonneg (u i - a)]

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

/-- When the projected datum is attained, the entire positive-parameter path
converges in norm to its minimum norm preimage. -/
theorem path_tendsto_of_minimum (T : H →L[ℝ] Y) (r : Y) (a : H)
    (ha : T a = BudgetProfile.projectedDatum T r)
    (hmin : ∀ x : H, T x = BudgetProfile.projectedDatum T r → ‖a‖ ≤ ‖x‖) :
    Tendsto (RegularizationLimits.path T r) (𝓝[>] (0 : ℝ)) (𝓝 a) := by
  have hbound : ∀ᶠ α : ℝ in 𝓝[>] 0, ‖RegularizationLimits.path T r α‖ ≤ ‖a‖ := by
    filter_upwards [RegularizationLimits.eventual_pos] with α hα
    rw [RegularizationLimits.path_of_pos T r hα]
    exact correction_norm_le T r hα a ha
  have hnorm := norm_tendsto_of_minimum T (BudgetProfile.projectedDatum T r) a hmin
    (RegularizationLimits.path T r)
    (RegularizationLimits.fitted_tendsto_projectedDatum T r) hbound
  apply tendsto_of_norm_energy_le (RegularizationLimits.path T r) a hnorm
  filter_upwards [RegularizationLimits.eventual_pos] with α hα
  rw [RegularizationLimits.path_of_pos T r hα]
  exact correction_distance_sq_le T r hα a ha

/-- WR08 attained case, constructing the unique minimum norm limit from range
membership rather than assuming its existence. -/
theorem exists_unique_minimum_and_limit (T : H →L[ℝ] Y) (r : Y)
    (hb : BudgetProfile.projectedDatum T r ∈ Set.range T) :
    ∃! a : H,
      (T a = BudgetProfile.projectedDatum T r ∧
        ∀ x : H, T x = BudgetProfile.projectedDatum T r → ‖a‖ ≤ ‖x‖) ∧
      Tendsto (RegularizationLimits.path T r) (𝓝[>] (0 : ℝ)) (𝓝 a) := by
  obtain ⟨a, ha, huniq⟩ :=
    exists_unique_minimum_preimage T (BudgetProfile.projectedDatum T r) hb
  refine ⟨a, ⟨ha, path_tendsto_of_minimum T r a ha.1 ha.2⟩, ?_⟩
  intro x hx
  exact huniq x hx.1

end KomorebiSpace.RegularizationStrongLimit
