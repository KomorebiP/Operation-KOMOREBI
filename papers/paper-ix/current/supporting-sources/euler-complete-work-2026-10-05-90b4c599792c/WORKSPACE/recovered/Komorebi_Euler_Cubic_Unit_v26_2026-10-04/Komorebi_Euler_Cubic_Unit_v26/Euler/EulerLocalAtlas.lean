module
public import Euler.LocalRootTransport
public import Euler.TerminalConsequences
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

def eulerWallBeforeChart (r i : ℕ) (hr : 0 < r) : Series :=
  skeletonBeforeSeries (residualTerminalIndex r) i (terminalWallDistance r)
    (terminalUpperSeries r hr) (terminalLowerSeries r hr)

def eulerWallAfterChart (r i : ℕ) (hr : 0 < r) : Series :=
  skeletonAfterSeries (residualTerminalIndex r) i (terminalWallDistance r)
    (terminalUpperSeries r hr) (terminalLowerSeries r hr)

lemma eulerWallBeforeChart_restricted (r i : ℕ) (hr : 0 < r) :
    Restricted (eulerWallBeforeChart r i hr) := skeletonBeforeSeries_restricted _ _ _ _ _

lemma eulerWallAfterChart_restricted (r i : ℕ) (hr : 0 < r) :
    Restricted (eulerWallAfterChart r i hr) := skeletonAfterSeries_restricted _ _ _ _ _

/-- Exact chart equality for the actual Euler-defined normalized residual. -/
theorem eulerWall_before_chart (r i : ℕ) (hr : 0 < r) (hi : i < residualTerminalIndex r)
    (hd : terminalWallDistance r≤skeletonContent (residualTerminalIndex r) i) (y : D) :
    reval (eulerNormalizedResidual r hr)
      (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
    (2:D)^(terminalWallDistance r)*reval (eulerWallBeforeChart r i hr) y := by
  rw [dyadicChart,eulerNormalizedResidual_terminal_form r hr (by omega)]
  exact skeletonBeforeSeries_normalization _ _ _ hi hd
    (terminalUpperSeries_restricted r hr) (terminalLowerSeries_restricted r hr) y

/-- At and after the threshold the normalization is the skeleton's exact content. -/
theorem eulerWall_after_chart (r i : ℕ) (hr : 0 < r) (hi : i < residualTerminalIndex r)
    (hd : skeletonContent (residualTerminalIndex r) i≤terminalWallDistance r) (y : D) :
    reval (eulerNormalizedResidual r hr)
      (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
    (2:D)^(skeletonContent (residualTerminalIndex r) i)*reval (eulerWallAfterChart r i hr) y := by
  rw [dyadicChart,eulerNormalizedResidual_terminal_form r hr (by omega)]
  exact skeletonAfterSeries_normalization _ _ _ hi hd
    (terminalUpperSeries_restricted r hr) (terminalLowerSeries_restricted r hr) y

lemma eulerWallBeforeChart_red (r i : ℕ) (hr : 0 < r)
    (hd : terminalWallDistance r < skeletonContent (residualTerminalIndex r) i)
    (hv : red (reval (terminalLowerSeries r hr) (i:D))=1) :
    PowerSeries.map red (eulerWallBeforeChart r i hr)=1 :=
  skeletonBeforeSeries_red _ _ _ _ _ hd hv

lemma eulerWallAfterChart_red (r i : ℕ) (hr : 0 < r)
    (hd : skeletonContent (residualTerminalIndex r) i≤terminalWallDistance r)
    (hv : red (reval (terminalLowerSeries r hr) (i:D))=1) :
    PowerSeries.map red (eulerWallAfterChart r i hr)=
      X+C (if terminalWallDistance r=skeletonContent (residualTerminalIndex r) i then 1 else 0) :=
  skeletonAfterSeries_red _ _ _ hd (terminalUpperSeries_restricted r hr)
    (terminalUpperSeries_red r hr) hv

/-- Every subthreshold Euler skeleton ball with odd lower value is root-free. -/
theorem eulerWall_subthreshold_norm (r i : ℕ) (hr : 0 < r)
    (hi : i < residualTerminalIndex r)
    (hd : terminalWallDistance r < skeletonContent (residualTerminalIndex r) i)
    (hv : red (reval (terminalLowerSeries r hr) (i:D))=1)
    (x : D) (hx : x∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i)) :
    ‖reval (eulerNormalizedResidual r hr) x‖=‖(2:D)^(terminalWallDistance r)‖ := by
  obtain ⟨y,rfl⟩ := hx
  rw [eulerWall_before_chart r i hr hi (by omega),norm_mul,
    restricted_norm_one_of_map (eulerWallBeforeChart_restricted r i hr)
      (eulerWallBeforeChart_red r i hr hd hv),mul_one]

theorem eulerWall_subthreshold_nonzero (r i : ℕ) (hr : 0 < r)
    (hi : i < residualTerminalIndex r)
    (hd : terminalWallDistance r < skeletonContent (residualTerminalIndex r) i)
    (hv : red (reval (terminalLowerSeries r hr) (i:D))=1)
    (x : D) (hx : x∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i)) :
    reval (eulerNormalizedResidual r hr) x≠0 := by
  intro hz
  have hn := eulerWall_subthreshold_norm r i hr hi hd hv x hx
  rw [hz,norm_zero] at hn
  exact (norm_ne_zero_iff.mpr (pow_ne_zero _ (by norm_num : (2:D)≠0))) hn.symm

/-- End-to-end local Euler atlas: existence, uniqueness, derivative, and exact distance law. -/
theorem eulerWall_superthreshold_atlas (r i : ℕ) (hr : 0 < r)
    (hi : i < residualTerminalIndex r)
    (hd : skeletonContent (residualTerminalIndex r) i≤terminalWallDistance r)
    (hv : red (reval (terminalLowerSeries r hr) (i:D))=1) :
    ∃ α:D, α∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i) ∧
      reval (eulerNormalizedResidual r hr) α=0 ∧
      ‖deriv (qeval (eulerNormalizedResidual r hr)) (α:ℚ_[2])‖=
        ‖(2:D)^(skeletonSlope (residualTerminalIndex r) i)‖ ∧
      (∀ x∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i),
        reval (eulerNormalizedResidual r hr) x=0 ↔ x=α) ∧
      (∀ x∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i),
        ‖reval (eulerNormalizedResidual r hr) x‖=
          ‖(2:D)^(skeletonSlope (residualTerminalIndex r) i)‖*‖x-α‖) := by
  exact restricted_scaled_root_atlas (eulerNormalizedResidual_restricted r hr)
    (eulerWallAfterChart_restricted r i hr) (i:D)
    (skeletonDepth (residualTerminalIndex r) i) (skeletonSlope (residualTerminalIndex r) i)
    (skeletonDepth_pos _ _) _ (eulerWallAfterChart_red r i hr hd hv)
    (eulerWall_after_chart r i hr hi hd)

/-- The root displacement is exact, including the equality-wall scale. -/
theorem eulerWall_superthreshold_displacement (r i : ℕ) (hr : 0 < r)
    (hi : i < residualTerminalIndex r)
    (hd : skeletonContent (residualTerminalIndex r) i≤terminalWallDistance r)
    (hv : red (reval (terminalLowerSeries r hr) (i:D))=1) :
    ∃ α:D, α∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i) ∧
      reval (eulerNormalizedResidual r hr) α=0 ∧
      ‖α-(i:D)‖=‖(2:D)^(terminalWallDistance r-skeletonSlope (residualTerminalIndex r) i)‖ := by
  have hn : ‖reval (terminalLowerSeries r hr) (i:D)‖=1 := by
    apply res_nonzero_norm_one
    rw [res_eq_red,hv]
    decide
  have hzero : ‖reval (eulerWallAfterChart r i hr) 0‖=
      ‖(2:D)^(terminalWallDistance r-skeletonContent (residualTerminalIndex r) i)‖ := by
    rw [eulerWallAfterChart,skeletonAfterSeries_reval _ _ _ (terminalLowerSeries_restricted r hr)]
    simp only [zero_mul,zero_add,mul_zero,add_zero,norm_mul,hn,mul_one]
  have hh:=restricted_scaled_root_displacement (eulerNormalizedResidual_restricted r hr)
    (eulerWallAfterChart_restricted r i hr) (i:D)
    (skeletonDepth (residualTerminalIndex r) i) (skeletonSlope (residualTerminalIndex r) i)
    (terminalWallDistance r-skeletonContent (residualTerminalIndex r) i)
    (skeletonDepth_pos _ _) _ (eulerWallAfterChart_red r i hr hd hv)
    (eulerWall_after_chart r i hr hi hd) hzero
  have he : skeletonDepth (residualTerminalIndex r) i+
      (terminalWallDistance r-skeletonContent (residualTerminalIndex r) i)=
      terminalWallDistance r-skeletonSlope (residualTerminalIndex r) i := by
    unfold skeletonContent at hd ⊢
    omega
  simpa only [he] using hh

end Komorebi.Euler
