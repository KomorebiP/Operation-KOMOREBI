module
public import Euler.EulerSlopeAtlas
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

/-- Lower valuation smaller than the ball depth gives a constant residue chart. -/
def eulerShallowLowerChart (r i s : ℕ) (hr : 0<r) (w : D) : Series :=
  normalizedLowerChart (terminalLowerSeries r hr) (i:D)
    (skeletonDepth (residualTerminalIndex r) i) s w

lemma eulerShallowLowerChart_restricted (r i s : ℕ) (hr : 0<r) (w : D) :
    Restricted (eulerShallowLowerChart r i s hr w) :=
  normalizedLowerChart_restricted _ _ _ _ _ (skeletonDepth_pos _ _)

lemma eulerShallowLowerChart_red (r i s : ℕ) (hr : 0<r) (w : D)
    (hs : s<skeletonDepth (residualTerminalIndex r) i) (hw : red w=1) :
    PowerSeries.map red (eulerShallowLowerChart r i s hr w)=1 := by
  rw [eulerShallowLowerChart,normalizedLowerChart_red_shallow _ _ _ _ _ hs,hw,map_one]

lemma eulerShallowLowerChart_reval (r i s : ℕ) (hr : 0<r) (w : D)
    (hs : s≤skeletonDepth (residualTerminalIndex r) i)
    (hw : reval (terminalLowerSeries r hr) (i:D)=(2:D)^s*w) (y : D) :
    reval (terminalLowerSeries r hr)
      (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
    (2:D)^s*reval (eulerShallowLowerChart r i s hr w) y :=
  normalizedLowerChart_reval (terminalLowerSeries_restricted r hr) _ _ _ _
    (skeletonDepth_pos _ _) hs hw y

/-- Both local charts are formed from the actual Euler factors. -/
def eulerShallowBeforeChart (r i s : ℕ) (hr : 0<r) (w : D) : Series :=
  slopeBeforeSeries (skeletonContent (residualTerminalIndex r) i) (terminalWallDistance r+s)
    (skeletonLocalSeries (residualTerminalIndex r) i (terminalUpperSeries r hr))
    (eulerShallowLowerChart r i s hr w)

def eulerShallowAfterChart (r i s : ℕ) (hr : 0<r) (w : D) : Series :=
  slopeAfterSeries (skeletonContent (residualTerminalIndex r) i) (terminalWallDistance r+s)
    (skeletonLocalSeries (residualTerminalIndex r) i (terminalUpperSeries r hr))
    (eulerShallowLowerChart r i s hr w)

lemma eulerShallowBeforeChart_restricted (r i s : ℕ) (hr : 0<r) (w : D) :
    Restricted (eulerShallowBeforeChart r i s hr w) :=
  slopeBeforeSeries_restricted _ _ (skeletonLocalSeries_restricted _ _ _)
    (eulerShallowLowerChart_restricted r i s hr w)

lemma eulerShallowAfterChart_restricted (r i s : ℕ) (hr : 0<r) (w : D) :
    Restricted (eulerShallowAfterChart r i s hr w) :=
  slopeAfterSeries_restricted _ _ (skeletonLocalSeries_restricted _ _ _)
    (eulerShallowLowerChart_restricted r i s hr w)

theorem eulerShallow_before_chart (r i s : ℕ) (hr : 0<r)
    (hi : i<residualTerminalIndex r) (w : D)
    (hs : s≤skeletonDepth (residualTerminalIndex r) i)
    (hw : reval (terminalLowerSeries r hr) (i:D)=(2:D)^s*w)
    (hd : terminalWallDistance r+s≤skeletonContent (residualTerminalIndex r) i) (y : D) :
    reval (eulerNormalizedResidual r hr)
      (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
    (2:D)^(terminalWallDistance r+s)*reval (eulerShallowBeforeChart r i s hr w) y := by
  rw [dyadicChart,eulerNormalizedResidual_terminal_form r hr (by omega),
    skeletonLocalSeries_factorization _ _ hi (terminalUpperSeries_restricted r hr)]
  rw [show reval (terminalLowerSeries r hr)
    ((i:D)+(2:D)^(skeletonDepth (residualTerminalIndex r) i)*y)=
    (2:D)^s*reval (eulerShallowLowerChart r i s hr w) y from
      eulerShallowLowerChart_reval r i s hr w hs hw y]
  rw [eulerShallowBeforeChart,slopeBeforeSeries_reval _ _
    (skeletonLocalSeries_restricted _ _ _) (eulerShallowLowerChart_restricted r i s hr w)]
  have hh : (2:D)^(skeletonContent (residualTerminalIndex r) i)=
      (2:D)^(terminalWallDistance r+s)*
      (2:D)^(skeletonContent (residualTerminalIndex r) i-(terminalWallDistance r+s)) := by
    rw [← pow_add,Nat.add_sub_of_le hd]
  rw [hh,pow_add]
  ring

theorem eulerShallow_after_chart (r i s : ℕ) (hr : 0<r)
    (hi : i<residualTerminalIndex r) (w : D)
    (hs : s≤skeletonDepth (residualTerminalIndex r) i)
    (hw : reval (terminalLowerSeries r hr) (i:D)=(2:D)^s*w)
    (hd : skeletonContent (residualTerminalIndex r) i≤terminalWallDistance r+s) (y : D) :
    reval (eulerNormalizedResidual r hr)
      (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
    (2:D)^(skeletonContent (residualTerminalIndex r) i)*
      reval (eulerShallowAfterChart r i s hr w) y := by
  rw [dyadicChart,eulerNormalizedResidual_terminal_form r hr (by omega),
    skeletonLocalSeries_factorization _ _ hi (terminalUpperSeries_restricted r hr)]
  rw [show reval (terminalLowerSeries r hr)
    ((i:D)+(2:D)^(skeletonDepth (residualTerminalIndex r) i)*y)=
    (2:D)^s*reval (eulerShallowLowerChart r i s hr w) y from
      eulerShallowLowerChart_reval r i s hr w hs hw y]
  rw [eulerShallowAfterChart,slopeAfterSeries_reval _ _
    (skeletonLocalSeries_restricted _ _ _) (eulerShallowLowerChart_restricted r i s hr w)]
  have hh : (2:D)^(terminalWallDistance r+s)=
      (2:D)^(skeletonContent (residualTerminalIndex r) i)*
      (2:D)^(terminalWallDistance r+s-skeletonContent (residualTerminalIndex r) i) := by
    rw [← pow_add,Nat.add_sub_of_le hd]
  rw [← mul_assoc ((2:D)^(terminalWallDistance r)),← pow_add,hh]
  ring

lemma eulerShallowBeforeChart_red (r i s : ℕ) (hr : 0<r) (w : D)
    (hs : s<skeletonDepth (residualTerminalIndex r) i) (hw : red w=1)
    (hd : terminalWallDistance r+s<skeletonContent (residualTerminalIndex r) i) :
    PowerSeries.map red (eulerShallowBeforeChart r i s hr w)=1 := by
  rw [eulerShallowBeforeChart,slopeBeforeSeries_red _ _ _ _ hd,
    eulerShallowLowerChart_red r i s hr w hs hw]

lemma eulerShallowAfterChart_red (r i s : ℕ) (hr : 0<r) (w : D)
    (hs : s<skeletonDepth (residualTerminalIndex r) i) (hw : red w=1)
    (hd : skeletonContent (residualTerminalIndex r) i≤terminalWallDistance r+s) :
    PowerSeries.map red (eulerShallowAfterChart r i s hr w)=
      X+C (if terminalWallDistance r+s=skeletonContent (residualTerminalIndex r) i
        then 1 else 0) := by
  rw [eulerShallowAfterChart,slopeAfterSeries,map_add,map_mul,map_X,
    skeletonLocalSeries_red _ _ (terminalUpperSeries_restricted r hr)
      (terminalUpperSeries_red r hr),mul_one,map_mul,map_C,
    eulerShallowLowerChart_red r i s hr w hs hw,mul_one,map_pow,red_two]
  by_cases he : terminalWallDistance r+s=skeletonContent (residualTerminalIndex r) i
  · simp [he]
  · simp [he,show terminalWallDistance r+s-skeletonContent (residualTerminalIndex r) i≠0 by omega]

/-- When the center content is below the radius, the whole ball has a complete atlas. -/
theorem eulerShallow_dichotomy (r i s : ℕ) (hr : 0<r)
    (hi : i<residualTerminalIndex r) (w : D)
    (hs : s<skeletonDepth (residualTerminalIndex r) i)
    (hw : reval (terminalLowerSeries r hr) (i:D)=(2:D)^s*w) (hu : red w=1) :
    (terminalWallDistance r+s<skeletonContent (residualTerminalIndex r) i ∧
      ∀ x∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i),
        ‖reval (eulerNormalizedResidual r hr) x‖=‖(2:D)^(terminalWallDistance r+s)‖) ∨
    (skeletonContent (residualTerminalIndex r) i≤terminalWallDistance r+s ∧
      SimpleBallAtlas (eulerNormalizedResidual r hr) (i:D)
        (skeletonDepth (residualTerminalIndex r) i) (skeletonSlope (residualTerminalIndex r) i)) := by
  by_cases hd : terminalWallDistance r+s<skeletonContent (residualTerminalIndex r) i
  · refine Or.inl ⟨hd,?_⟩
    rintro x ⟨y,rfl⟩
    rw [eulerShallow_before_chart r i s hr hi w (le_of_lt hs) hw (le_of_lt hd),norm_mul,
      restricted_norm_one_of_map (eulerShallowBeforeChart_restricted r i s hr w)
        (eulerShallowBeforeChart_red r i s hr w hs hu hd),mul_one]
  · have hd' : skeletonContent (residualTerminalIndex r) i≤terminalWallDistance r+s := by omega
    refine Or.inr ⟨hd',?_⟩
    exact restricted_scaled_root_atlas (eulerNormalizedResidual_restricted r hr)
      (eulerShallowAfterChart_restricted r i s hr w) (i:D)
      (skeletonDepth (residualTerminalIndex r) i) (skeletonSlope (residualTerminalIndex r) i)
      (skeletonDepth_pos _ _) _ (eulerShallowAfterChart_red r i s hr w hs hu hd')
      (eulerShallow_after_chart r i s hr hi w (le_of_lt hs) hw hd')

theorem eulerShallow_no_critical (r i s : ℕ) (hr : 0<r)
    (hi : i<residualTerminalIndex r) (w : D)
    (hs : s<skeletonDepth (residualTerminalIndex r) i)
    (hw : reval (terminalLowerSeries r hr) (i:D)=(2:D)^s*w) (hu : red w=1)
    (x:D) (hx : x∈dyadicBall (i:D) (skeletonDepth (residualTerminalIndex r) i))
    (hz : reval (eulerNormalizedResidual r hr) x=0) :
    deriv (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])≠0 := by
  rcases eulerShallow_dichotomy r i s hr hi w hs hw hu with ⟨_,hn⟩ | ⟨_,hat⟩
  · have he:=hn x hx
    rw [hz,norm_zero] at he
    exact False.elim ((norm_ne_zero_iff.mpr (pow_ne_zero _ two_ne_zero)) he.symm)
  · exact simpleBallAtlas_no_critical hat x hx hz

end Komorebi.Euler
