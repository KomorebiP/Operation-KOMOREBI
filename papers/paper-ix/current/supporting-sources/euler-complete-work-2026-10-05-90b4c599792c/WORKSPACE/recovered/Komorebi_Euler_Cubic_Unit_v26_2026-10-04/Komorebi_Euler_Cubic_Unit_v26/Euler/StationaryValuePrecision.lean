module
public import Euler.QuadraticCriticalValue
@[expose] public section
noncomputable section
set_option maxHeartbeats 600000
namespace Komorebi.Euler
open PowerSeries

lemma quadraticCriticalSeries_distance (b : D) (u : Dˣ) (R : Series)
    (hR : Restricted R) (x:D) :
    ‖reval (quadraticCriticalSeries b (u:D) R) x‖=
      ‖x-quadraticCriticalPoint b u R hR‖ := by
  obtain ⟨c,hc,_,huniq,hdist⟩:=restricted_affine_atlas
    (quadraticCritical_restricted b (u:D) hR) (red b)
    (quadraticCritical_red b (u:D) (qc_unit_red u) R)
  have he : quadraticCriticalPoint b u R hR=c :=
    (huniq _).mp (quadraticCriticalPoint_spec b u R hR).2.2
  rw [he]
  exact hdist x

lemma qc_cubicTail_rjet {R:Series} (hR:Restricted R) (x:D) :
    rjet 1 ((X:Series)^3*R) x=x^2*criticalTailSlope R x := by
  rw [rjet_one_mul (qc_Xpow_restricted 3) hR,qc_reval_Xpow]
  have hp : rjet 1 ((X:Series)^3) x=3*x^2 := by
    have h:=rjet_one_polynomial ((Polynomial.X:Polynomial D)^3) x
    convert h using 1 <;> norm_num
  rw [hp]
  unfold criticalTailSlope
  ring

/-- At the actual critical point, the nonquadratic value error gains two factors of distance. -/
lemma quadraticStationary_quadratic_error (a b : D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (x:D) :
    let c:=quadraticCriticalPoint b u R hR
    ‖reval (quadraticCoreSeries a b (u:D) R) x-quadraticCriticalValue a b u R hR-
      (u:D)*(x-c)^2‖≤(1/4:ℝ)*‖x-c‖^2 := by
  dsimp only
  let c:=quadraticCriticalPoint b u R hR
  have hH:=PowerSeries.isRestricted.mul 1 (qc_Xpow_restricted 3) hR
  have herr:=reval_first_order_error hH c x
  rw [reval_mul (qc_Xpow_restricted 3) hR,reval_mul (qc_Xpow_restricted 3) hR,
    qc_reval_Xpow,qc_reval_Xpow,qc_cubicTail_rjet hR] at herr
  have hc:=(quadraticCriticalPoint_spec b u R hR).2.2
  rw [quadraticCritical_reval b (u:D) hR] at hc
  change b+(u:D)*c+2*c^2*criticalTailSlope R c=0 at hc
  rw [quadraticCriticalValue,quadraticCore_reval a b (u:D) hR,
    quadraticCore_reval a b (u:D) hR]
  change ‖(a+2*b*x+(u:D)*x^2+4*x^3*reval R x)-
    (a+2*b*c+(u:D)*c^2+4*c^3*reval R c)-(u:D)*(x-c)^2‖≤_
  have he : (a+2*b*x+(u:D)*x^2+4*x^3*reval R x)-
      (a+2*b*c+(u:D)*c^2+4*c^3*reval R c)-(u:D)*(x-c)^2=
      4*(x^3*reval R x-c^3*reval R c-(x-c)*(c^2*criticalTailSlope R c)) := by
    linear_combination 2*(x-c)*hc
  rw [he,norm_mul,qc_norm_four]
  exact mul_le_mul_of_nonneg_left herr (by norm_num)

/-- Exact stationary value precision: no generic big-O remainder is left. -/
theorem quadraticStationary_value_distance (a b : D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (x:D) :
    ‖reval (quadraticCoreSeries a b (u:D) R) x-quadraticCriticalValue a b u R hR‖=
      ‖x-quadraticCriticalPoint b u R hR‖^2 := by
  let c:=quadraticCriticalPoint b u R hR
  by_cases hx:x=c
  · subst x
    simp [quadraticCriticalValue,c]
  have hp:0<‖x-c‖^2 := sq_pos_of_pos (norm_pos_iff.mpr (sub_ne_zero.mpr hx))
  have herr:=quadraticStationary_quadratic_error a b u R hR x
  change ‖reval (quadraticCoreSeries a b (u:D) R) x-quadraticCriticalValue a b u R hR-
    (u:D)*(x-c)^2‖≤(1/4:ℝ)*‖x-c‖^2 at herr
  have hs : ‖reval (quadraticCoreSeries a b (u:D) R) x-quadraticCriticalValue a b u R hR-
      (u:D)*(x-c)^2‖<‖(u:D)*(x-c)^2‖ := by
    rw [norm_mul,PadicInt.norm_units,one_mul,norm_pow]
    exact herr.trans_lt (by nlinarith)
  have hn:=PadicInt.norm_eq_of_norm_add_lt_right
    (z1:=reval (quadraticCoreSeries a b (u:D) R) x-quadraticCriticalValue a b u R hR)
    (z2:=-((u:D)*(x-c)^2)) (by simpa only [←sub_eq_add_neg,norm_neg] using hs)
  simpa only [norm_neg,norm_mul,PadicInt.norm_units,one_mul,norm_pow] using hn

/-- The observable half-slope gives the EXACT critical-value error at any trial point. -/
theorem quadraticStationary_value_slope (a b : D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (x:D) :
    ‖reval (quadraticCoreSeries a b (u:D) R) x-quadraticCriticalValue a b u R hR‖=
      ‖reval (quadraticCriticalSeries b (u:D) R) x‖^2 := by
  rw [quadraticStationary_value_distance,quadraticCriticalSeries_distance]

/-- All value/slope tests concern the actual infinite series and actual moved critical value. -/
theorem quadraticStationary_nonzero_of_norm_mismatch (a b : D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (x:D)
    (hneq:‖reval (quadraticCoreSeries a b (u:D) R) x‖≠
      ‖reval (quadraticCriticalSeries b (u:D) R) x‖^2) :
    quadraticCriticalValue a b u R hR≠0 := by
  intro hz
  have he:=quadraticStationary_value_slope a b u R hR x
  rw [hz,sub_zero] at he
  exact hneq he

/-- Soundness of a finite value-and-slope nonvanishing test, once its norms are certified. -/
theorem quadraticCore_no_critical_of_norm_mismatch (a b : D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (x:D)
    (hneq:‖reval (quadraticCoreSeries a b (u:D) R) x‖≠
      ‖reval (quadraticCriticalSeries b (u:D) R) x‖^2) (y:D) :
    ¬CriticalZero (qeval (quadraticCoreSeries a b (u:D) R)) (y:ℚ_[2]) := by
  intro hy
  exact quadraticStationary_nonzero_of_norm_mismatch a b u R hR x hneq
    ((quadraticCriticalValue_zero_iff a b u R hR).mp ⟨y,hy⟩)

/-- If the critical value is zero, the whole core has an exact double-distance norm law. -/
theorem quadraticCore_double_distance_of_critical (a b : D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (hz:quadraticCriticalValue a b u R hR=0) (x:D) :
    ‖reval (quadraticCoreSeries a b (u:D) R) x‖=
      ‖x-quadraticCriticalPoint b u R hR‖^2 := by
  simpa only [hz,sub_zero] using quadraticStationary_value_distance a b u R hR x

end Komorebi.Euler
