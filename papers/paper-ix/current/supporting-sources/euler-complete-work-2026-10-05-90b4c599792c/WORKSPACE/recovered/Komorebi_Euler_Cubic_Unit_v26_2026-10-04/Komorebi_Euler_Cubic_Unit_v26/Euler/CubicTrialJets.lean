module
public import Euler.CubicCriticalValues
@[expose] public section
noncomputable section
set_option maxHeartbeats 700000
namespace Komorebi.Euler
open PowerSeries

/-- The observable second Hasse jet measures the exact distance to the inflection point. -/
theorem cubicInflection_halfSecond_distance (a b c:D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (x:D) :
    ‖rjet 2 (cubicCoreSeries a b c (u:D) R) x‖=‖x-cubicInflectionPoint c u R hR‖ := by
  have h := rjet_one_hasseSeries (cubicCore_restricted a b c (u:D) hR) 1 x
  rw [cubicCore_hasse_one,quadraticCore_rjet_one b c (3*(u:D))
    (cubicDerivativeTail_restricted hR)] at h
  have he : rjet 2 (cubicCoreSeries a b c (u:D) R) x =
      reval (quadraticCriticalSeries c (3*(u:D)) (cubicDerivativeTail R)) x := by
    apply cancel_two
    simpa only [Nat.cast_one,show (1:D)+1=2 by norm_num] using h.symm
  rw [he,←cubicSlopeUnit_val u]
  exact quadraticCriticalSeries_distance c (cubicSlopeUnit u) (cubicDerivativeTail R)
    (cubicDerivativeTail_restricted hR) x

/-- Certified trial-value precision at the inflection point. Unlike a quadratic critical
center, its value generally changes to first order. -/
theorem cubicInflection_trial_value_error (a b c:D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (x:D) :
    ‖reval (cubicCoreSeries a b c (u:D) R) x-
      reval (cubicCoreSeries a b c (u:D) R) (cubicInflectionPoint c u R hR)‖ ≤
      max (‖rjet 2 (cubicCoreSeries a b c (u:D) R) x‖*
        ‖rjet 1 (cubicCoreSeries a b c (u:D) R) x‖)
        (‖rjet 2 (cubicCoreSeries a b c (u:D) R) x‖^3) := by
  let f:=cubicCoreSeries a b c (u:D) R
  let ρ:=cubicInflectionPoint c u R hR
  let h:=ρ-x
  have hf:Restricted f:=cubicCore_restricted a b c (u:D) hR
  have hn:‖rjet 2 f x‖=‖h‖ := by
    simpa only [f,h,ρ,norm_sub_rev] using cubicInflection_halfSecond_distance a b c u R hR x
  have herr:=reval_second_order_error hf x ρ
  let e:=reval f ρ-reval f x-h*rjet 1 f x-h^2*rjet 2 f x
  have he:‖e‖≤‖h‖^3:=herr
  have hq:‖h^2*rjet 2 f x‖=‖h‖^3 := by rw [norm_mul,norm_pow,hn];ring
  have ha:‖h^2*rjet 2 f x+e‖≤‖h‖^3 :=
    (IsUltrametricDist.norm_add_le_max _ _).trans (max_le hq.le he)
  have hi:reval f ρ-reval f x=h*rjet 1 f x+(h^2*rjet 2 f x+e) := by dsimp [e];ring
  change ‖reval f x-reval f ρ‖≤max (‖rjet 2 f x‖*‖rjet 1 f x‖) (‖rjet 2 f x‖^3)
  rw [norm_sub_rev,hi,hn]
  exact (IsUltrametricDist.norm_add_le_max _ _).trans
    (max_le_max (by rw [norm_mul]) ha)

/-- A finite value/slope/curvature test implies the exact inflection criterion.
All three strict-error conditions must be certified; equality is inconclusive. -/
theorem cubicCore_no_critical_of_trial_jets (a b c:D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (x:D)
    (hs:‖rjet 2 (cubicCoreSeries a b c (u:D) R) x‖^2 <
      ‖rjet 1 (cubicCoreSeries a b c (u:D) R) x‖)
    (hv:max (‖rjet 2 (cubicCoreSeries a b c (u:D) R) x‖*
        ‖rjet 1 (cubicCoreSeries a b c (u:D) R) x‖)
        (‖rjet 2 (cubicCoreSeries a b c (u:D) R) x‖^3) <
      ‖reval (cubicCoreSeries a b c (u:D) R) x‖)
    (hm:‖reval (cubicCoreSeries a b c (u:D) R) x‖^2 ≠
      (1/4:ℝ)*‖rjet 1 (cubicCoreSeries a b c (u:D) R) x‖^3) (y:D) :
    ¬CriticalZero (qeval (cubicCoreSeries a b c (u:D) R)) (y:ℚ_[2]) := by
  let f:=cubicCoreSeries a b c (u:D) R
  let ρ:=cubicInflectionPoint c u R hR
  have hsd:=cubicInflection_slope_distance a b c u R hR x
  rw [←cubicInflection_halfSecond_distance a b c u R hR x] at hsd
  have hsn:‖rjet 1 f ρ‖=‖rjet 1 f x‖ := by
    have ht:‖rjet 1 f ρ-rjet 1 f x‖<‖rjet 1 f x‖ := by
      rw [norm_sub_rev]
      exact hsd.trans_lt hs
    have hh:=PadicInt.norm_eq_of_norm_add_lt_right (z1:=rjet 1 f ρ) (z2:=-rjet 1 f x)
      (by simpa only [←sub_eq_add_neg,norm_neg] using ht)
    simpa only [norm_neg] using hh
  have hvn:‖reval f ρ‖=‖reval f x‖ := by
    have ht:‖reval f ρ-reval f x‖<‖reval f x‖ := by
      rw [norm_sub_rev]
      exact (cubicInflection_trial_value_error a b c u R hR x).trans_lt hv
    have hh:=PadicInt.norm_eq_of_norm_add_lt_right (z1:=reval f ρ) (z2:=-reval f x)
      (by simpa only [←sub_eq_add_neg,norm_neg] using ht)
    simpa only [norm_neg] using hh
  apply cubicCore_no_critical_of_inflection_mismatch a b c u R hR _ y
  change ‖reval f ρ‖^2≠(1/4:ℝ)*‖rjet 1 f ρ‖^3
  rwa [hvn,hsn]

end Komorebi.Euler
