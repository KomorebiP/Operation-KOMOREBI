module
public import Euler.QuadraticPerturbationGap
public import Euler.EulerNearestCore
@[expose] public section
noncomputable section
set_option maxHeartbeats 500000
namespace Komorebi.Euler
open PowerSeries

lemma quadraticCore_coeff_high (a b u:D) (R:Series) (n:ℕ) :
    coeff (n+3) (quadraticCoreSeries a b u R)=4*coeff n R := by
  simp only [quadraticCoreSeries,map_add,coeff_C_mul,mul_assoc,coeff_X_pow_mul']
  simp [coeff_X,coeff_X_pow,
    show n+3≠1 by omega,show n+3≠2 by omega]

/-- Construct the tail rather than assuming it: an exact four-geometric coefficient law
produces an integral restricted R and an exact quadratic-core representation. -/
theorem fourTail_quadraticCore_representation (F:Series) (w:ℕ→D) (b u:D)
    (h1:coeff 1 F=2*b) (h2:coeff 2 F=u)
    (hw:∀n:ℕ,coeff (n+3) F=4*(4:D)^n*w n) :
    ∃R:Series, Restricted R ∧
      F=quadraticCoreSeries (coeff 0 F) b u R := by
  let R:Series:=rescale (4:D) (PowerSeries.mk w)
  refine ⟨R,restricted_rescale_four _,?_⟩
  ext n
  rcases n with _ | _ | _ | n
  · simp [quadraticCoreSeries,mul_assoc]
  · simpa [quadraticCoreSeries,mul_assoc,coeff_X_pow_mul'] using h1
  · simpa [quadraticCoreSeries,mul_assoc,coeff_X_pow_mul'] using h2
  · rw [show n+1+1+1=n+3 by omega,quadraticCore_coeff_high,hw]
    simp only [R,coeff_rescale,coeff_mk]
    ring

/-- An actual one-neighbor Euler core has the stronger quadratic representation;
when its linear coefficient is even the critical-point theorem applies directly. -/
theorem eulerOneNeighbor_critical_representation (r i:ℕ) (hr:0<r)
    (hj:4≤residualTerminalIndex r) (hi:i<residualTerminalIndex r)
    (hnear:¬HasTwoNearest (residualTerminalIndex r) i) (w:D) (F:Series)
    (hd:terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (hF:C (2:D)*F=eulerSlopeAfterChart r i hr w)
    (h1:red (coeff 1 F)=0) :
    ∃b:D, ∃u:Dˣ, ∃R:Series, Restricted R ∧
      F=quadraticCoreSeries (coeff 0 F) b (u:D) R := by
  obtain ⟨e,t,ε,he,hε,hc,hcoeff⟩ :=
    eulerSlope_oneNeighbor_coefficients r i hr hj hi hnear w F hd hF
  obtain ⟨b,hb⟩:=(red_eq_zero_iff _).mp h1
  have hu0:red (coeff 2 F)=1 := (directOne_lastOdd e t F w ε he hε hc).1
  have hu:IsUnit (coeff 2 F) := PadicInt.isUnit_iff.mpr
    (res_nonzero_norm_one _ (by rw [res_eq_red,hu0];decide))
  let u:Dˣ:=hu.unit
  have huval:(u:D)=coeff 2 F:=hu.unit_spec
  let wn:ℕ→D:=fun n=>2*(coeff (n+2) e+coeff (n+2) t)+ε*coeff (n+1) e
  have hw:∀n:ℕ,coeff (n+3) F=4*(4:D)^n*wn n := by
    intro n
    have hh:=hcoeff (n+1)
    rw [show n+1+2=n+3 by omega,pow_succ] at hh
    simpa only [wn,show n+1+1=n+2 by omega,mul_comm,mul_left_comm,mul_assoc] using hh
  obtain ⟨R,hR,hrep⟩:=fourTail_quadraticCore_representation F wn b (u:D) hb huval.symm hw
  exact ⟨b,u,R,hR,hrep⟩

/-- Complete construction of the critical scalar for this actual Euler core.
The scalar is not assumed to be nonzero. -/
theorem eulerOneNeighbor_movingCriticalValue (r i:ℕ) (hr:0<r)
    (hj:4≤residualTerminalIndex r) (hi:i<residualTerminalIndex r)
    (hnear:¬HasTwoNearest (residualTerminalIndex r) i) (w:D) (F:Series)
    (hd:terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (hF:C (2:D)*F=eulerSlopeAfterChart r i hr w)
    (h1:red (coeff 1 F)=0) :
    ∃b:D, ∃u:Dˣ, ∃R:Series, ∃hR:Restricted R,
      F=quadraticCoreSeries (coeff 0 F) b (u:D) R ∧
      (∀x:D, deriv (qeval F) (x:ℚ_[2])=0 ↔ x=quadraticCriticalPoint b u R hR) ∧
      ((∃x:D,CriticalZero (qeval F) (x:ℚ_[2])) ↔
        quadraticCriticalValue (coeff 0 F) b u R hR=0) := by
  obtain ⟨b,u,R,hR,hrep⟩:=eulerOneNeighbor_critical_representation r i hr hj hi hnear w F hd hF h1
  refine ⟨b,u,R,hR,hrep,?_,?_⟩
  · intro x
    conv_lhs => rw [hrep]
    exact quadraticCriticalPoint_unique (coeff 0 F) b u R hR x
  · have hh:=quadraticCriticalValue_zero_iff (coeff 0 F) b u R hR
    conv_lhs => rw [hrep]
    exact hh

/-- The new norm-gap certificate transfers to the original Euler residual on the exact
constructed local chart. This does not assert that every Euler coefficient passes the test. -/
theorem eulerQuadraticChart_no_critical_of_gap (r i:ℕ) (hr:0<r)
    (a b:D) (u:Dˣ) (R:Series) (hR:Restricted R)
    (hchart:∀y:D,reval (eulerNormalizedResidual r hr)
      (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=
      (2:D)^(skeletonContent (residualTerminalIndex r) i+1)*
        reval (quadraticCoreSeries a b (u:D) R) y)
    (hgap:(1/4:ℝ)*‖b‖^3<‖a-(↑(u⁻¹):D)*b^2‖) (y:D) :
    ¬(reval (eulerNormalizedResidual r hr)
       (dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y)=0 ∧
      deriv (qeval (eulerNormalizedResidual r hr))
       ((dyadicChart (i:D) (skeletonDepth (residualTerminalIndex r) i) y:D):ℚ_[2])=0) := by
  intro hc
  have he:=(restricted_scaled_critical_iff (eulerNormalizedResidual_restricted r hr)
    (quadraticCore_restricted a b (u:D) hR) (i:D)
    (skeletonDepth (residualTerminalIndex r) i)
    (skeletonContent (residualTerminalIndex r) i+1)
    (skeletonDepth_pos _ _) hchart y).mp hc
  apply quadraticCore_no_critical_of_gap a b u R hR hgap y
  refine ⟨?_,he.2⟩
  rw [← coe_reval (quadraticCore_restricted a b (u:D) hR),he.1]
  rfl

/-- If the linear coefficient is odd there is no critical point at all. -/
theorem quadraticLastOdd_oddLinear_slope (F:Series) (hF:Restricted F)
    (h2:LastOdd F 2) (h1:red (coeff 1 F)=1) (x:D) :
    ‖deriv (qeval F) (x:ℚ_[2])‖=1 := by
  have hm:PowerSeries.map red (hasseSeries 1 F)=1 := by
    ext n
    rw [coeff_map,coeff_hasseSeries]
    rcases n with _ | _ | n
    · simpa using h1
    · simp
    · have hh:=h2.2 (n+1+1+1) (by omega)
      simp only [map_mul,hh,mul_zero,coeff_one,show n+1+1≠0 by omega,ite_false]
  rw [deriv_qeval hF]
  change ‖reval (hasseSeries 1 F) x‖=1
  exact restricted_norm_one_of_map (restricted_hasseSeries hF 1) hm x

/-- Actual one-neighbor Euler cores have at most one critical point, whether or not
that point is a zero of the function. -/
theorem eulerOneNeighbor_atMostOne_critical (r i:ℕ) (hr:0<r)
    (hj:4≤residualTerminalIndex r) (hi:i<residualTerminalIndex r)
    (hnear:¬HasTwoNearest (residualTerminalIndex r) i) (w:D) (F:Series)
    (hd:terminalWallDistance r=skeletonSlope (residualTerminalIndex r) i)
    (hF:C (2:D)*F=eulerSlopeAfterChart r i hr w) (x y:D)
    (hx:deriv (qeval F) (x:ℚ_[2])=0) (hy:deriv (qeval F) (y:ℚ_[2])=0) : x=y := by
  rcases binary_value (red (coeff 1 F)) with h0 | h1
  · obtain ⟨b,u,R,hR,hrep⟩:=eulerOneNeighbor_critical_representation r i hr hj hi hnear w F hd hF h0
    have hxc: x=quadraticCriticalPoint b u R hR := by
      apply (quadraticCriticalPoint_unique (coeff 0 F) b u R hR x).mp
      simpa only [←hrep] using hx
    have hyc: y=quadraticCriticalPoint b u R hR := by
      apply (quadraticCriticalPoint_unique (coeff 0 F) b u R hR y).mp
      simpa only [←hrep] using hy
    exact hxc.trans hyc.symm
  · obtain ⟨e,t,ε,he,hε,hc,_⟩:=eulerSlope_oneNeighbor_coefficients r i hr hj hi hnear w F hd hF
    have hn:=quadraticLastOdd_oddLinear_slope F (directOne_restricted e t F w ε hc)
      (directOne_lastOdd e t F w ε he hε hc) h1 x
    rw [hx,norm_zero] at hn
    norm_num at hn

end Komorebi.Euler
