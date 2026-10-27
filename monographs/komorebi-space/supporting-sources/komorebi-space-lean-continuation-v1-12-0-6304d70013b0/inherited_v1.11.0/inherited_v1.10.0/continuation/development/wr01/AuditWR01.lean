import Mathlib.Analysis.InnerProductSpace.Adjoint
import Mathlib.Analysis.Normed.Module.WeakDual

/-!
# Bounded approximate realization (WR01)

The bounded approximation theorem for real Hilbert spaces, retaining the exact
norm budget. The proof uses weak-star compactness of the dual ball and the Riesz
isometric equivalence. It does not assume separability or a closed operator range,
and it does not assert strong convergence of the supplied candidates.
-/

noncomputable section

open Filter Set Metric Topology

namespace KomorebiSpace.BoundedApproximateRealization

variable {H Y : Type*}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]

/-- Even a frequently recurring budget bound is enough for exact realization.
This stronger filter form makes the full divergence-to-infinity corollary immediate. -/
theorem exists_solution_of_frequently_bounded
    (T : H →L[ℝ] Y) {ι : Type*} {l : Filter ι} [NeBot l]
    (u : ι → H) (r : Y) (M : ℝ)
    (hbound : ∃ᶠ i in l, ‖u i‖ ≤ M)
    (himage : Tendsto (fun i => T (u i)) l (𝓝 r)) :
    ∃ a : H, T a = r ∧ ‖a‖ ≤ M := by
  let v : ι → WeakDual ℝ H := fun i =>
    StrongDual.toWeakDual (InnerProductSpace.toDual ℝ H (u i))
  have hv : ∃ᶠ i in l,
      v i ∈ WeakDual.toStrongDual ⁻¹' closedBall (0 : StrongDual ℝ H) M := by
    exact hbound.mono fun i hi => by
      simpa [v, Metric.mem_closedBall, dist_eq_norm] using hi
  obtain ⟨φ, hφball, hφ⟩ :=
    (WeakDual.isCompact_closedBall (0 : StrongDual ℝ H) M).exists_mapClusterPt_of_frequently hv
  let a : H := (InnerProductSpace.toDual ℝ H).symm (WeakDual.toStrongDual φ)
  refine ⟨a, ?_, ?_⟩
  · apply ext_inner_right ℝ
    intro y
    have heval := hφ.continuousAt_comp (WeakDual.eval_continuous (T.adjoint y)).continuousAt
    have hlim : Tendsto (fun i => (v i) (T.adjoint y)) l (𝓝 (inner ℝ r y)) := by
      simpa only [v, StrongDual.toWeakDual_apply,
        InnerProductSpace.toDual_apply_apply, T.adjoint_inner_right] using
        himage.inner tendsto_const_nhds
    have heq : φ (T.adjoint y) = inner ℝ r y :=
      eq_of_nhds_neBot (heval.clusterPt.mono hlim).neBot
    simpa only [a, ← T.adjoint_inner_right, InnerProductSpace.toDual_symm_apply,
      WeakDual.toStrongDual_apply] using heq
  · have hnorm : ‖WeakDual.toStrongDual φ‖ ≤ M := by
      simpa only [Set.mem_preimage, Metric.mem_closedBall, dist_eq_norm, sub_zero] using hφball
    simpa only [a, LinearIsometryEquiv.norm_map] using hnorm

/-- WR01, including preservation of the same uniform norm budget. -/
theorem exists_solution_of_bounded_approximation
    (T : H →L[ℝ] Y) (u : ℕ → H) (r : Y) (M : ℝ)
    (hbound : ∀ n, ‖u n‖ ≤ M)
    (himage : Tendsto (fun n => T (u n)) atTop (𝓝 r)) :
    ∃ a : H, T a = r ∧ ‖a‖ ≤ M :=
  exists_solution_of_frequently_bounded T u r M
    (Filter.Eventually.of_forall hbound).frequently himage

/-- WR01 in the residual norm formulation printed in the monograph. -/
theorem exists_solution_of_bounded_residual_tendsto_zero
    (T : H →L[ℝ] Y) (u : ℕ → H) (r : Y) (M : ℝ)
    (hbound : ∀ n, ‖u n‖ ≤ M)
    (hresidual : Tendsto (fun n => ‖T (u n) - r‖) atTop (𝓝 0)) :
    ∃ a : H, T a = r ∧ ‖a‖ ≤ M := by
  apply exists_solution_of_bounded_approximation T u r M hbound
  exact tendsto_iff_norm_sub_tendsto_zero.mpr hresidual

/-- Exact solvability is equivalent to existence of a bounded approximating sequence. -/
theorem mem_range_iff_bounded_approximation (T : H →L[ℝ] Y) (r : Y) :
    r ∈ Set.range T ↔
      ∃ (u : ℕ → H) (M : ℝ), (∀ n, ‖u n‖ ≤ M) ∧
        Tendsto (fun n => ‖T (u n) - r‖) atTop (𝓝 0) := by
  constructor
  · rintro ⟨a, rfl⟩
    refine ⟨fun _ => a, ‖a‖, fun _ => le_rfl, ?_⟩
    simpa only [sub_self, norm_zero] using
      (tendsto_const_nhds : Tendsto (fun _ : ℕ => (0 : ℝ)) atTop (𝓝 0))
  · rintro ⟨u, M, hbound, hresidual⟩
    obtain ⟨a, ha, _⟩ :=
      exists_solution_of_bounded_residual_tendsto_zero T u r M hbound hresidual
    exact ⟨a, ha⟩

/-- For unattained data, every approximating sequence escapes every finite norm budget.
No closed-range assumption is used, and the conclusion is convergence to infinity,
not merely failure of a uniform bound. -/
theorem norm_tendsto_atTop_of_not_mem_range
    (T : H →L[ℝ] Y) (u : ℕ → H) (r : Y)
    (hr : r ∉ Set.range T)
    (himage : Tendsto (fun n => T (u n)) atTop (𝓝 r)) :
    Tendsto (fun n => ‖u n‖) atTop atTop := by
  apply Filter.tendsto_atTop.mpr
  intro M
  by_contra h
  have hfreq : ∃ᶠ n in atTop, ‖u n‖ ≤ M := by
    exact (Filter.not_eventually.mp h).mono fun n hn => (lt_of_not_ge hn).le
  obtain ⟨a, ha, _⟩ := exists_solution_of_frequently_bounded T u r M hfreq himage
  exact hr ⟨a, ha⟩

end KomorebiSpace.BoundedApproximateRealization

#print axioms KomorebiSpace.BoundedApproximateRealization.exists_solution_of_frequently_bounded
#print axioms KomorebiSpace.BoundedApproximateRealization.exists_solution_of_bounded_approximation
#print axioms KomorebiSpace.BoundedApproximateRealization.exists_solution_of_bounded_residual_tendsto_zero
#print axioms KomorebiSpace.BoundedApproximateRealization.mem_range_iff_bounded_approximation
#print axioms KomorebiSpace.BoundedApproximateRealization.norm_tendsto_atTop_of_not_mem_range
