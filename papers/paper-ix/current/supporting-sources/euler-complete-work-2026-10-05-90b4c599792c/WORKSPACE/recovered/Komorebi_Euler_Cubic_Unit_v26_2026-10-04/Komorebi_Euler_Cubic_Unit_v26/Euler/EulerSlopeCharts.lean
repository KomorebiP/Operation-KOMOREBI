module
public import Euler.SlopeChartSeries
public import Euler.EulerLocalAtlas
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

/-- The actual lower Euler prefix divided by the radius of a chosen skeleton ball. -/
def eulerLowerRootChart (r i : ℕ) (hr : 0<r) (w : D) : Series :=
  normalizedLowerChart (terminalLowerSeries r hr) (i:D)
    (skeletonDepth (residualTerminalIndex r) i)
    (skeletonDepth (residualTerminalIndex r) i) w

lemma eulerLowerRootChart_restricted (r i : ℕ) (hr : 0<r) (w : D) :
    Restricted (eulerLowerRootChart r i hr w) :=
  normalizedLowerChart_restricted _ _ _ _ _ (skeletonDepth_pos _ _)

lemma eulerLowerRootChart_red (r i : ℕ) (hr : 0<r) (w : D)
    (hd : red (rjet 1 (terminalLowerSeries r hr) (i:D))=1) :
    PowerSeries.map red (eulerLowerRootChart r i hr w)=X+C (red w) :=
  normalizedLowerChart_red_root _ _ _ _ (skeletonDepth_pos _ _) hd

lemma eulerLowerRootChart_reval (r i : ℕ) (hr : 0<r) (w : D)
    (hw : reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w) (y : D) :
    reval (terminalLowerSeries r hr)
      (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
    (2:D)^(skeletonDepth (residualTerminalIndex r) i)*
      reval (eulerLowerRootChart r i hr w) y :=
  normalizedLowerChart_reval (terminalLowerSeries_restricted r hr) _ _ _ _
    (skeletonDepth_pos _ _) (le_refl _) hw y

/-- Lower-slope-dominated chart of the actual Euler wall. -/
def eulerSlopeBeforeChart (r i : ℕ) (hr : 0<r) (w : D) : Series :=
  slopeBeforeSeries (skeletonSlope (residualTerminalIndex r) i) (terminalWallDistance r)
    (skeletonLocalSeries (residualTerminalIndex r) i (terminalUpperSeries r hr))
    (eulerLowerRootChart r i hr w)

/-- Skeleton-slope-dominated chart, also used at equal slopes. -/
def eulerSlopeAfterChart (r i : ℕ) (hr : 0<r) (w : D) : Series :=
  slopeAfterSeries (skeletonSlope (residualTerminalIndex r) i) (terminalWallDistance r)
    (skeletonLocalSeries (residualTerminalIndex r) i (terminalUpperSeries r hr))
    (eulerLowerRootChart r i hr w)

lemma eulerSlopeBeforeChart_restricted (r i : ℕ) (hr : 0<r) (w : D) :
    Restricted (eulerSlopeBeforeChart r i hr w) :=
  slopeBeforeSeries_restricted _ _ (skeletonLocalSeries_restricted _ _ _)
    (eulerLowerRootChart_restricted r i hr w)

lemma eulerSlopeAfterChart_restricted (r i : ℕ) (hr : 0<r) (w : D) :
    Restricted (eulerSlopeAfterChart r i hr w) :=
  slopeAfterSeries_restricted _ _ (skeletonLocalSeries_restricted _ _ _)
    (eulerLowerRootChart_restricted r i hr w)

/-- Exact normalization before slope equality. No hypothesized normal form is supplied. -/
theorem eulerSlope_before_chart (r i : ℕ) (hr : 0<r)
    (hi : i<residualTerminalIndex r) (w : D)
    (hw : reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w)
    (hd : terminalWallDistance r≤skeletonSlope (residualTerminalIndex r) i) (y : D) :
    reval (eulerNormalizedResidual r hr)
      (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
    (2:D)^(skeletonDepth (residualTerminalIndex r) i+terminalWallDistance r)*
      reval (eulerSlopeBeforeChart r i hr w) y := by
  rw [dyadicChart,eulerNormalizedResidual_terminal_form r hr (by omega),
    skeletonLocalSeries_factorization _ _ hi (terminalUpperSeries_restricted r hr)]
  rw [show reval (terminalLowerSeries r hr)
      ((i:D)+(2:D)^(skeletonDepth (residualTerminalIndex r) i)*y)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*
        reval (eulerLowerRootChart r i hr w) y from
        eulerLowerRootChart_reval r i hr w hw y]
  rw [eulerSlopeBeforeChart,slopeBeforeSeries_reval _ _
    (skeletonLocalSeries_restricted _ _ _) (eulerLowerRootChart_restricted r i hr w)]
  exact slopeBefore_normalization _ _ _ hd _ _ _

/-- Exact normalization after slope equality, including equality itself. -/
theorem eulerSlope_after_chart (r i : ℕ) (hr : 0<r)
    (hi : i<residualTerminalIndex r) (w : D)
    (hw : reval (terminalLowerSeries r hr) (i:D)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*w)
    (hd : skeletonSlope (residualTerminalIndex r) i≤terminalWallDistance r) (y : D) :
    reval (eulerNormalizedResidual r hr)
      (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
    (2:D)^(skeletonDepth (residualTerminalIndex r) i+
      skeletonSlope (residualTerminalIndex r) i)*
      reval (eulerSlopeAfterChart r i hr w) y := by
  rw [dyadicChart,eulerNormalizedResidual_terminal_form r hr (by omega),
    skeletonLocalSeries_factorization _ _ hi (terminalUpperSeries_restricted r hr)]
  rw [show reval (terminalLowerSeries r hr)
      ((i:D)+(2:D)^(skeletonDepth (residualTerminalIndex r) i)*y)=
      (2:D)^(skeletonDepth (residualTerminalIndex r) i)*
        reval (eulerLowerRootChart r i hr w) y from
        eulerLowerRootChart_reval r i hr w hw y]
  rw [eulerSlopeAfterChart,slopeAfterSeries_reval _ _
    (skeletonLocalSeries_restricted _ _ _) (eulerLowerRootChart_restricted r i hr w)]
  exact slopeAfter_normalization _ _ _ hd _ _ _

lemma eulerSlopeBeforeChart_red (r i : ℕ) (hr : 0<r) (w : D)
    (hd : terminalWallDistance r<skeletonSlope (residualTerminalIndex r) i)
    (hjet : red (rjet 1 (terminalLowerSeries r hr) (i:D))=1) :
    PowerSeries.map red (eulerSlopeBeforeChart r i hr w)=X+C (red w) := by
  rw [eulerSlopeBeforeChart,slopeBeforeSeries_red _ _ _ _ hd,
    eulerLowerRootChart_red r i hr w hjet]

lemma eulerSlopeAfterChart_red (r i : ℕ) (hr : 0<r) (w : D)
    (hd : skeletonSlope (residualTerminalIndex r) i<terminalWallDistance r) :
    PowerSeries.map red (eulerSlopeAfterChart r i hr w)=X := by
  exact slopeAfterSeries_red _ _ _ _ hd
    (skeletonLocalSeries_red _ _ (terminalUpperSeries_restricted r hr)
      (terminalUpperSeries_red r hr))

lemma eulerSlopeEqualChart_red (r i : ℕ) (hr : 0<r) (w : D)
    (hd : terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (hjet : red (rjet 1 (terminalLowerSeries r hr) (i:D))=1) :
    PowerSeries.map red (eulerSlopeAfterChart r i hr w)=C (red w) := by
  unfold eulerSlopeAfterChart
  rw [hd]
  exact slopeEqualSeries_red _ _ _ _
    (skeletonLocalSeries_red _ _ (terminalUpperSeries_restricted r hr)
      (terminalUpperSeries_red r hr))
    (eulerLowerRootChart_red r i hr w hjet)

end Komorebi.Euler
