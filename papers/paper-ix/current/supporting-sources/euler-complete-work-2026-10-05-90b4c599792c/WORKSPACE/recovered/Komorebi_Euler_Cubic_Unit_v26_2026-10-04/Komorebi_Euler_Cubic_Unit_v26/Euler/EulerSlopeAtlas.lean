module
public import Euler.EulerSlopeCharts
public import Euler.EulerLocalRows
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

/-- Bundling the explicit root, uniqueness, derivative norm and full distance law.
This is a conclusion proved below, not an assumed normal form of the Euler residual. -/
def SimpleBallAtlas (g : Series) (a : D) (k d : ℕ) : Prop :=
  ∃ α:D, α∈dyadicBall a k ∧ reval g α=0 ∧
    ‖deriv (qeval g) (α:ℚ_[2])‖=‖(2:D)^d‖ ∧
    (∀ x∈dyadicBall a k, reval g x=0 ↔ x=α) ∧
    (∀ x∈dyadicBall a k, ‖reval g x‖=‖(2:D)^d‖*‖x-α‖)

lemma simpleBallAtlas_no_critical {g : Series} {a : D} {k d : ℕ}
    (h : SimpleBallAtlas g a k d) (x : D) (hx : x∈dyadicBall a k)
    (hz : reval g x=0) : deriv (qeval g) (x:ℚ_[2])≠0 := by
  obtain ⟨α,_,_,hd,hu,_⟩ := h
  have he := (hu x hx).mp hz
  subst x
  intro hzero
  rw [hzero,norm_zero] at hd
  exact (norm_ne_zero_iff.mpr (pow_ne_zero d two_ne_zero)) hd.symm

/-- The normalized lower chart constructs an actual unique lower root on the whole ball. -/
theorem eulerLower_root_atlas (r i : ℕ) (hr : 0<r) (w : D)
    (hw : reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w)
    (hjet : red (rjet 1 (terminalLowerSeries r hr) (i:D))=1) :
    SimpleBallAtlas (terminalLowerSeries r hr) (i:D)
      (skeletonDepth (residualTerminalIndex r) i) 0 := by
  apply restricted_scaled_root_atlas (terminalLowerSeries_restricted r hr)
    (eulerLowerRootChart_restricted r i hr w) (i:D)
    (skeletonDepth (residualTerminalIndex r) i) 0 (skeletonDepth_pos _ _) (red w)
    (eulerLowerRootChart_red r i hr w hjet)
  intro y
  simpa only [Nat.add_zero] using eulerLowerRootChart_reval r i hr w hw y

/-- Below slope equality, the original Euler root has lower-slope order delta. -/
theorem eulerSlope_before_atlas (r i : ℕ) (hr : 0<r)
    (hi : i<residualTerminalIndex r) (w : D)
    (hw : reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w)
    (hjet : red (rjet 1 (terminalLowerSeries r hr) (i:D))=1)
    (hd : terminalWallDistance r<skeletonSlope (residualTerminalIndex r) i) :
    SimpleBallAtlas (eulerNormalizedResidual r hr) (i:D)
      (skeletonDepth (residualTerminalIndex r) i) (terminalWallDistance r) := by
  exact restricted_scaled_root_atlas (eulerNormalizedResidual_restricted r hr)
    (eulerSlopeBeforeChart_restricted r i hr w) (i:D)
    (skeletonDepth (residualTerminalIndex r) i) (terminalWallDistance r)
    (skeletonDepth_pos _ _) (red w) (eulerSlopeBeforeChart_red r i hr w hd hjet)
    (eulerSlope_before_chart r i hr hi w hw (le_of_lt hd))

/-- Above slope equality, the root has exactly the skeleton-slope order. -/
theorem eulerSlope_after_atlas (r i : ℕ) (hr : 0<r)
    (hi : i<residualTerminalIndex r) (w : D)
    (hw : reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w)
    (hd : skeletonSlope (residualTerminalIndex r) i<terminalWallDistance r) :
    SimpleBallAtlas (eulerNormalizedResidual r hr) (i:D)
      (skeletonDepth (residualTerminalIndex r) i)
      (skeletonSlope (residualTerminalIndex r) i) := by
  apply restricted_scaled_root_atlas (eulerNormalizedResidual_restricted r hr)
    (eulerSlopeAfterChart_restricted r i hr w) (i:D)
    (skeletonDepth (residualTerminalIndex r) i) (skeletonSlope (residualTerminalIndex r) i)
    (skeletonDepth_pos _ _) 0
    (by simpa using eulerSlopeAfterChart_red r i hr w hd)
    (eulerSlope_after_chart r i hr hi w hw (le_of_lt hd))

/-- Every nonmatching slope gives an exact simple atlas, with the minimum slope. -/
theorem eulerSlope_nonresonant_atlas (r i : ℕ) (hr : 0<r)
    (hi : i<residualTerminalIndex r) (w : D)
    (hw : reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w)
    (hjet : red (rjet 1 (terminalLowerSeries r hr) (i:D))=1)
    (hd : terminalWallDistance r≠skeletonSlope (residualTerminalIndex r) i) :
    SimpleBallAtlas (eulerNormalizedResidual r hr) (i:D)
      (skeletonDepth (residualTerminalIndex r) i)
      (min (terminalWallDistance r) (skeletonSlope (residualTerminalIndex r) i)) := by
  rcases lt_or_gt_of_ne hd with h | h
  · rw [min_eq_left (le_of_lt h)]
    exact eulerSlope_before_atlas r i hr hi w hw hjet h
  · rw [min_eq_right (le_of_lt h)]
    exact eulerSlope_after_atlas r i hr hi w hw h

/-- At equal slopes, the next alignment bit can exclude the entire root ball. -/
theorem eulerSlope_equal_odd_norm (r i : ℕ) (hr : 0<r)
    (hi : i<residualTerminalIndex r) (w : D)
    (hw : reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w)
    (hjet : red (rjet 1 (terminalLowerSeries r hr) (i:D))=1)
    (hd : terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (hodd : red w=1) (x:D)
    (hx : x∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i)) :
    ‖reval (eulerNormalizedResidual r hr) x‖=
      ‖(2:D)^(skeletonContent (residualTerminalIndex r) i)‖ := by
  obtain ⟨y,rfl⟩ := hx
  rw [eulerSlope_after_chart r i hr hi w hw (le_of_eq hd.symm),norm_mul]
  have hmap : PowerSeries.map red (eulerSlopeAfterChart r i hr w)=1 := by
    rw [eulerSlopeEqualChart_red r i hr w hd hjet,hodd,map_one]
  rw [restricted_norm_one_of_map (eulerSlopeAfterChart_restricted r i hr w) hmap,mul_one]
  rfl

/-- The exceptional even core is constructed as an integral restricted series.
This statement neither supplies its degree nor asserts that it has any root. -/
theorem eulerSlope_equal_even_core (r i : ℕ) (hr : 0<r)
    (hi : i<residualTerminalIndex r) (w : D)
    (hw : reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w)
    (hjet : red (rjet 1 (terminalLowerSeries r hr) (i:D))=1)
    (hd : terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (heven : red w=0) :
    ∃ F:Series, Restricted F ∧ C (2:D)*F=eulerSlopeAfterChart r i hr w ∧
      ∀ y:D, reval (eulerNormalizedResidual r hr)
        (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
      (2:D)^(skeletonContent (residualTerminalIndex r) i+1)*reval F y := by
  have hmap : PowerSeries.map red (eulerSlopeAfterChart r i hr w)=0 := by
    rw [eulerSlopeEqualChart_red r i hr w hd hjet,heven,map_zero]
  obtain ⟨F,hF,hFr⟩ := restricted_divide_even
    (eulerSlopeAfterChart_restricted r i hr w) hmap
  refine ⟨F,hFr,hF,?_⟩
  intro y
  rw [eulerSlope_after_chart r i hr hi w hw (le_of_eq hd.symm),← hF,
    reval_C_mul hFr,pow_succ]
  simp only [skeletonContent,mul_assoc]

/-- On a lower-root ball a critical zero forces exact slope equality and even alignment. -/
theorem eulerSlope_critical_necessary (r i : ℕ) (hr : 0<r)
    (hi : i<residualTerminalIndex r) (w : D)
    (hw : reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w)
    (hjet : red (rjet 1 (terminalLowerSeries r hr) (i:D))=1)
    (x:D) (hx : x∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i))
    (hz : reval (eulerNormalizedResidual r hr) x=0)
    (hder : deriv (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])=0) :
    terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i ∧ red w=0 := by
  have hd : terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i := by
    by_contra hn
    exact simpleBallAtlas_no_critical
      (eulerSlope_nonresonant_atlas r i hr hi w hw hjet hn) x hx hz hder
  refine ⟨hd,?_⟩
  by_contra hn
  have hnrm := eulerSlope_equal_odd_norm r i hr hi w hw hjet hd
    (red_not_zero_eq_one w hn) x hx
  rw [hz,norm_zero] at hnrm
  exact (norm_ne_zero_iff.mpr (pow_ne_zero _ two_ne_zero)) hnrm.symm

end Komorebi.Euler
