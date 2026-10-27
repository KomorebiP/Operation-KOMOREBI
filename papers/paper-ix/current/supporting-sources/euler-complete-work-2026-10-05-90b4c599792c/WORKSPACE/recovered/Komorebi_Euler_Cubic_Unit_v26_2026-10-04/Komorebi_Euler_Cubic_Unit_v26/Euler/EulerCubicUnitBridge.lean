module
public import Euler.ScaledCubicUnitObstruction
public import Euler.CubicUnitCertificates
public import Euler.EulerCubicCriticalBridge
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

/-- Transport the scale-sensitive obstruction through an exact actual Euler chart.
The chart and arithmetic gap are explicit obligations, not asserted for all r. -/
theorem eulerCubicChart_no_critical_of_scaled_discriminant (r i:ℕ) (hr:0<r)
    (a b c:D) (u:Dˣ) (s:D) (R:Series) (hR:Restricted R)
    (hchart:∀y:D,reval (eulerNormalizedResidual r hr)
      (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
      (2:D)^(skeletonContent (residualTerminalIndex r) i+2)*
        reval (cubicCoreSeries a b c (u:D) (C s*R)) y)
    (hgap:let hRs:=PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 s) hR
      (1/256:ℝ)*‖s‖^2*‖rjet 1 (cubicCoreSeries a b c (u:D) (C s*R))
        (cubicInflectionPoint c u (C s*R) hRs)‖^7 <
      ‖cubicJetDiscriminant a b c u (C s*R) hRs‖^2)
    (y:D) : ¬(reval (eulerNormalizedResidual r hr)
      (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=0 ∧
      deriv (qeval (eulerNormalizedResidual r hr))
        ((dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y:D):ℚ_[2])=0) := by
  intro hc
  have hRs:Restricted (C s*R):=PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) hR
  have he:=(restricted_scaled_critical_iff (eulerNormalizedResidual_restricted r hr)
    (cubicCore_restricted a b c (u:D) hRs) (i:D)
    (skeletonDepth (residualTerminalIndex r) i)
    (skeletonContent (residualTerminalIndex r) i+2)
    (skeletonDepth_pos _ _) hchart y).mp hc
  apply cubicCore_no_critical_of_scaled_discriminant_gap a b c u s R hR hgap y
  refine ⟨?_,he.2⟩
  rw [←coe_reval (cubicCore_restricted a b c (u:D) hRs),he.1]
  rfl

end Komorebi.Euler
