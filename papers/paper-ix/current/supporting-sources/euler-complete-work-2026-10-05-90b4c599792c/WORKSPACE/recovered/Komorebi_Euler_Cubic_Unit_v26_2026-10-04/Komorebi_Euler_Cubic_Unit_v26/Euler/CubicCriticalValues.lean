module
public import Euler.CubicInflection
@[expose] public section
noncomputable section
set_option maxHeartbeats 900000
namespace Komorebi.Euler
open PowerSeries

/-- At any critical point, the value differs from the inflection value at exact cubic scale. -/
theorem cubicCritical_value_from_inflection (a b c:D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (x:D)
    (hx:deriv (qeval (cubicCoreSeries a b c (u:D) R)) (x:ℚ_[2])=0) :
    ‖reval (cubicCoreSeries a b c (u:D) R) x-
      reval (cubicCoreSeries a b c (u:D) R) (cubicInflectionPoint c u R hR)‖=
      (1/2:ℝ)*‖x-cubicInflectionPoint c u R hR‖^3 := by
  let ρ:=cubicInflectionPoint c u R hR
  let h:=x-ρ
  let T:Series:=(X:Series)^4*R
  have hT:Restricted T:=cubicTail_restricted hR
  let e1:D:=rjet 1 T x-rjet 1 T ρ-h*(2*rjet 2 T ρ)
  let e2:D:=reval T x-reval T ρ-h*rjet 1 T ρ-h^2*rjet 2 T ρ
  have he1:‖e1‖≤‖h‖^2 := by
    have hh:=reval_first_order_error (restricted_hasseSeries hT 1) ρ x
    rw [rjet_one_hasseSeries hT 1 ρ] at hh
    simpa [e1,h,rjet,show (1:D)+1=2 by norm_num] using hh
  have he2:‖e2‖≤‖h‖^3 := reval_second_order_error hT ρ x
  have hc:=cubicInflection_rjet_two a b c u R hR
  rw [cubicCore_rjet_two a b c (u:D) hR] at hc
  change c+3*(u:D)*ρ+4*rjet 2 T ρ=0 at hc
  rw [deriv_qeval (cubicCore_restricted a b c (u:D) hR),PadicInt.coe_eq_zero,
    cubicCore_rjet_one a b c (u:D) hR] at hx
  change b+2*c*x+3*(u:D)*x^2+4*rjet 1 T x=0 at hx
  have hid:reval (cubicCoreSeries a b c (u:D) R) x-
      reval (cubicCoreSeries a b c (u:D) R) ρ =
      -2*(u:D)*h^3+4*(e2-h*e1) := by
    rw [cubicCore_reval a b c (u:D) hR,cubicCore_reval a b c (u:D) hR]
    change (a+b*x+c*x^2+(u:D)*x^3+4*reval T x)-
      (a+b*ρ+c*ρ^2+(u:D)*ρ^3+4*reval T ρ) = _
    dsimp only [e1,e2,h]
    linear_combination (x-ρ)*hx-(x-ρ)^2*hc
  change ‖reval (cubicCoreSeries a b c (u:D) R) x-
    reval (cubicCoreSeries a b c (u:D) R) ρ‖=(1/2:ℝ)*‖h‖^3
  rw [hid]
  have he:‖e2-h*e1‖≤‖h‖^3 := by
    calc
      _ ≤ max ‖e2‖ ‖h*e1‖ := by
        simpa only [sub_eq_add_neg,norm_neg] using IsUltrametricDist.norm_add_le_max e2 (-(h*e1))
      _ ≤ ‖h‖^3 := max_le he2 (by
        rw [norm_mul]
        calc
          _ ≤ ‖h‖*‖h‖^2 := mul_le_mul_of_nonneg_left he1 (norm_nonneg _)
          _ = ‖h‖^3 := by ring)
  by_cases hh:h=0
  · have hz:e2-h*e1=0 := norm_eq_zero.mp
      (le_antisymm (by simpa only [hh,norm_zero,zero_pow (by decide : 3≠0)] using he)
        (norm_nonneg _))
    rw [hz]
    simp [hh]
  have hp:0<‖h‖^3 := pow_pos (norm_pos_iff.mpr hh) _
  have hn:‖2*(u:D)*h^3‖=(1/2:ℝ)*‖h‖^3 := by
    rw [norm_mul,norm_mul,norm_two,PadicInt.norm_units,mul_one,norm_pow]
  have hs:‖(4:D)*(e2-h*e1)‖<‖2*(u:D)*h^3‖ := by
    rw [norm_mul,qc_norm_four,hn]
    exact (mul_le_mul_of_nonneg_left he (by norm_num : (0:ℝ)≤1/4)).trans_lt (by nlinarith)
  have heq:=PadicInt.norm_eq_of_norm_add_lt_right
    (z1:=-2*(u:D)*h^3+4*(e2-h*e1)) (z2:=2*(u:D)*h^3) (by
      rw [show -2*(u:D)*h^3+4*(e2-h*e1)+2*(u:D)*h^3=4*(e2-h*e1) by ring]
      exact hs)
  exact heq.trans hn

/-- All critical points lie on the same norm sphere around the unique inflection point. -/
theorem cubicCritical_slope_radius (a b c:D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (x:D)
    (hx:deriv (qeval (cubicCoreSeries a b c (u:D) R)) (x:ℚ_[2])=0) :
    ‖rjet 1 (cubicCoreSeries a b c (u:D) R) (cubicInflectionPoint c u R hR)‖=
      ‖x-cubicInflectionPoint c u R hR‖^2 := by
  have h:=cubicInflection_slope_distance a b c u R hR x
  rw [deriv_qeval (cubicCore_restricted a b c (u:D) hR),PadicInt.coe_eq_zero] at hx
  simpa only [hx,zero_sub,norm_neg] using h

/-- A single inflection-centered value/slope norm mismatch excludes every repeated root.
This is a sufficient condition, not a necessary one. -/
theorem cubicCore_no_critical_of_inflection_mismatch (a b c:D) (u:Dˣ)
    (R:Series) (hR:Restricted R)
    (hm:‖reval (cubicCoreSeries a b c (u:D) R) (cubicInflectionPoint c u R hR)‖^2 ≠
      (1/4:ℝ)*‖rjet 1 (cubicCoreSeries a b c (u:D) R) (cubicInflectionPoint c u R hR)‖^3)
    (x:D) : ¬CriticalZero (qeval (cubicCoreSeries a b c (u:D) R)) (x:ℚ_[2]) := by
  rintro ⟨hx0,hx1⟩
  have hx:reval (cubicCoreSeries a b c (u:D) R) x=0 := by
    apply PadicInt.coe_eq_zero.mp
    simpa only [coe_reval (cubicCore_restricted a b c (u:D) hR)] using hx0
  have hv:=cubicCritical_value_from_inflection a b c u R hR x hx1
  have hs:=cubicCritical_slope_radius a b c u R hR x hx1
  rw [hx,zero_sub,norm_neg] at hv
  apply hm
  rw [hv,hs]
  ring

/-- If the derivative vanishes at the inflection point, there is no other critical point. -/
theorem cubicCore_unique_critical_of_inflection_zero (a b c:D) (u:Dˣ)
    (R:Series) (hR:Restricted R)
    (hz:rjet 1 (cubicCoreSeries a b c (u:D) R) (cubicInflectionPoint c u R hR)=0)
    (x:D) : deriv (qeval (cubicCoreSeries a b c (u:D) R)) (x:ℚ_[2])=0 ↔
      x=cubicInflectionPoint c u R hR := by
  constructor
  · intro hx
    have hh:=cubicCritical_slope_radius a b c u R hR x hx
    rw [hz,norm_zero] at hh
    exact sub_eq_zero.mp (norm_eq_zero.mp ((pow_eq_zero_iff (by decide : 2≠0)).mp hh.symm))
  · intro hx
    rw [hx,deriv_qeval (cubicCore_restricted a b c (u:D) hR),hz]
    rfl

/-- Triple-jet degeneracy reduces to TWO exact inflection data, not a sampled cubic discriminant. -/
theorem cubicCore_triple_zero_iff (a b c:D) (u:Dˣ) (R:Series) (hR:Restricted R) :
    (∃x:D,qeval (cubicCoreSeries a b c (u:D) R) (x:ℚ_[2])=0 ∧
      deriv (qeval (cubicCoreSeries a b c (u:D) R)) (x:ℚ_[2])=0 ∧
      deriv (deriv (qeval (cubicCoreSeries a b c (u:D) R))) (x:ℚ_[2])=0) ↔
    reval (cubicCoreSeries a b c (u:D) R) (cubicInflectionPoint c u R hR)=0 ∧
    rjet 1 (cubicCoreSeries a b c (u:D) R) (cubicInflectionPoint c u R hR)=0 := by
  constructor
  · rintro ⟨x,h0,h1,h2⟩
    have hx:=(cubicInflection_unique a b c u R hR x).mp h2
    subst x
    rw [←coe_reval (cubicCore_restricted a b c (u:D) hR),PadicInt.coe_eq_zero] at h0
    rw [deriv_qeval (cubicCore_restricted a b c (u:D) hR),PadicInt.coe_eq_zero] at h1
    exact ⟨h0,h1⟩
  · rintro ⟨h0,h1⟩
    refine ⟨cubicInflectionPoint c u R hR,?_,?_,(cubicInflection_unique a b c u R hR _).mpr rfl⟩
    · rw [←coe_reval (cubicCore_restricted a b c (u:D) hR),h0];rfl
    · rw [deriv_qeval (cubicCore_restricted a b c (u:D) hR),h1];rfl

end Komorebi.Euler
