module
public import Euler.CubicCriticalValues
public import Euler.EulerCriticalValueBridge
@[expose] public section
noncomputable section
set_option maxHeartbeats 700000
namespace Komorebi.Euler
open PowerSeries

lemma cubicCore_coeff_high (a b c u:D) (R:Series) (n:ℕ) :
    coeff (n+4) (cubicCoreSeries a b c u R)=4*coeff n R := by
  simp only [cubicCoreSeries,map_add,coeff_C_mul,mul_assoc,coeff_X_pow_mul']
  simp [coeff_X,coeff_X_pow,show n+4≠1 by omega,show n+4≠2 by omega,show n+4≠3 by omega]

/-- Construct the integral restricted tail from a complete coefficient identity. -/
theorem fourTail_cubicCore_representation (F:Series) (w:ℕ→D) (u:D)
    (h3:coeff 3 F=u) (hw:∀n:ℕ,coeff (n+4) F=4*(4:D)^n*w n) :
    ∃R:Series, Restricted R ∧
      F=cubicCoreSeries (coeff 0 F) (coeff 1 F) (coeff 2 F) u R := by
  let R:Series:=rescale (4:D) (PowerSeries.mk w)
  refine ⟨R,restricted_rescale_four _,?_⟩
  ext n
  rcases n with _ | _ | _ | _ | n
  · simp [cubicCoreSeries,mul_assoc]
  · simp [cubicCoreSeries,mul_assoc,coeff_X_pow_mul']
  · simp [cubicCoreSeries,mul_assoc,coeff_X_pow_mul']
  · simpa [cubicCoreSeries,mul_assoc,coeff_X_pow_mul'] using h3
  · rw [show n+1+1+1+1=n+4 by omega,cubicCore_coeff_high,hw]
    simp only [R,coeff_rescale,coeff_mk]
    ring

/-- The cubic class is derived from the ACTUAL Euler two-neighbor half-core. -/
theorem eulerTwoNeighbor_cubicCritical_representation (r i:ℕ) (hr:0<r)
    (hj:4≤residualTerminalIndex r) (hi:i<residualTerminalIndex r)
    (hnear:HasTwoNearest (residualTerminalIndex r) i) (w:D) (F K:Series)
    (hd:terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (hF:C (2:D)*F=eulerSlopeAfterChart r i hr w) (hK:C (2:D)*K=F) :
    ∃u:Dˣ, ∃R:Series, Restricted R ∧
      K=cubicCoreSeries (coeff 0 K) (coeff 1 K) (coeff 2 K) (u:D) R := by
  obtain ⟨e,t,he,hc,_⟩:=eulerSlope_twoNeighbor_coefficients r i hr hj hi hnear w F hd hF
  have ho:=directTwo_divided_lastOdd e t F K w he hc hK
  have hu:IsUnit (coeff 3 K) := PadicInt.isUnit_iff.mpr
    (res_nonzero_norm_one _ (by rw [res_eq_red,ho.1];decide))
  let u:Dˣ:=hu.unit
  have huval:(u:D)=coeff 3 K:=hu.unit_spec
  let wn:ℕ→D:=fun n=>4*(coeff (n+3) e+coeff (n+3) t)-coeff (n+1) e
  have hw:∀n:ℕ,coeff (n+4) K=4*(4:D)^n*wn n := by
    intro n
    have hh:=directTwo_divided_coeff e t F K w hc hK (n+1)
    rw [show n+1+3=n+4 by omega,pow_succ] at hh
    simpa only [wn,show n+1+2=n+3 by omega,mul_comm,mul_left_comm,mul_assoc] using hh
  obtain ⟨R,hR,hrep⟩:=fourTail_cubicCore_representation K wn (u:D) huval.symm hw
  exact ⟨u,R,hR,hrep⟩

/-- The actual cubic Euler core cannot have two different critical zeros. -/
theorem eulerTwoNeighbor_criticalZero_unique (r i:ℕ) (hr:0<r)
    (hj:4≤residualTerminalIndex r) (hi:i<residualTerminalIndex r)
    (hnear:HasTwoNearest (residualTerminalIndex r) i) (w:D) (F K:Series)
    (hd:terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (hF:C (2:D)*F=eulerSlopeAfterChart r i hr w) (hK:C (2:D)*K=F)
    (x y:D) (hx:CriticalZero (qeval K) (x:ℚ_[2]))
    (hy:CriticalZero (qeval K) (y:ℚ_[2])) : x=y := by
  obtain ⟨u,R,hR,hrep⟩:=eulerTwoNeighbor_cubicCritical_representation r i hr hj hi hnear w F K hd hF hK
  rw [hrep] at hx hy
  exact cubicCore_critical_zero_unique _ _ _ u hR x y hx hy

/-- A norm mismatch at the CONSTRUCTED inflection point excludes all critical zeros of
an actual Euler cubic core. The mismatch itself remains an arithmetic obligation. -/
theorem eulerCubicChart_no_critical_of_inflection_mismatch (r i:ℕ) (hr:0<r)
    (a b c:D) (u:Dˣ) (R:Series) (hR:Restricted R)
    (hchart:∀y:D,reval (eulerNormalizedResidual r hr)
      (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
      (2:D)^(skeletonContent (residualTerminalIndex r) i+2)*
        reval (cubicCoreSeries a b c (u:D) R) y)
    (hgap:‖reval (cubicCoreSeries a b c (u:D) R) (cubicInflectionPoint c u R hR)‖^2 ≠
      (1/4:ℝ)*‖rjet 1 (cubicCoreSeries a b c (u:D) R) (cubicInflectionPoint c u R hR)‖^3)
    (y:D) : ¬(reval (eulerNormalizedResidual r hr)
      (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=0 ∧
      deriv (qeval (eulerNormalizedResidual r hr))
        ((dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y:D):ℚ_[2])=0) := by
  intro hc
  have he:=(restricted_scaled_critical_iff (eulerNormalizedResidual_restricted r hr)
    (cubicCore_restricted a b c (u:D) hR) (i:D)
    (skeletonDepth (residualTerminalIndex r) i)
    (skeletonContent (residualTerminalIndex r) i+2)
    (skeletonDepth_pos _ _) hchart y).mp hc
  apply cubicCore_no_critical_of_inflection_mismatch a b c u R hR hgap y
  refine ⟨?_,he.2⟩
  rw [←coe_reval (cubicCore_restricted a b c (u:D) hR),he.1]
  rfl

end Komorebi.Euler
