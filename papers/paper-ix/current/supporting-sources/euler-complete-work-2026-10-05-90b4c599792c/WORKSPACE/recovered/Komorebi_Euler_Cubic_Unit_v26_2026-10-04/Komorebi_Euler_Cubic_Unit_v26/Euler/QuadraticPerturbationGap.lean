module
public import Euler.StationaryValuePrecision
@[expose] public section
noncomputable section
set_option maxHeartbeats 400000
namespace Komorebi.Euler
open PowerSeries

/-- Quantitative moving-critical-value bound for an arbitrary integral analytic tail.
The parameter is epsilon=4e, the linear coefficient is epsilon*b1, and the
constant coefficient is epsilon*c0+epsilon^2*c1. The quadratic coefficient is any unit. -/
theorem quadraticPerturbation_critical_error (e c0 c1 b1:D) (u:Dˣ)
    (R:Series) (hR:Restricted R) :
    ‖quadraticCriticalValue (4*e*c0+16*e^2*c1) (2*e*b1) u R hR-4*e*c0‖≤
      (1/4:ℝ)*‖e‖^2 := by
  let a:D:=4*e*c0+16*e^2*c1
  let b:D:=2*e*b1
  let main:D:=a-(↑(u⁻¹):D)*b^2
  have he:=quadraticCriticalValue_error a b u R hR
  have heb:‖b‖≤(1/2:ℝ)*‖e‖ := by
    dsimp [b]
    rw [norm_mul,norm_mul,norm_two]
    exact mul_le_of_le_one_right (mul_nonneg (by norm_num) (norm_nonneg _))
      (PadicInt.norm_le_one _)
  have hb1:‖b‖≤1:=PadicInt.norm_le_one _
  have he1:‖e‖≤1:=PadicInt.norm_le_one _
  have hb0:0≤‖b‖:=norm_nonneg _
  have he0:0≤‖e‖:=norm_nonneg _
  have herr:‖quadraticCriticalValue a b u R hR-main‖≤(1/4:ℝ)*‖e‖^2 := by
    apply he.trans
    have hb_le:‖b‖≤‖e‖:=by linarith
    have hs:‖b‖^2≤‖e‖^2:=pow_le_pow_left₀ hb0 hb_le 2
    have ht:‖b‖^3≤‖b‖^2:=by nlinarith [sq_nonneg ‖b‖]
    nlinarith
  have hmain:‖main-4*e*c0‖≤(1/4:ℝ)*‖e‖^2 := by
    have hid:main-4*e*c0=4*e^2*(4*c1-(↑(u⁻¹):D)*b1^2) := by
      dsimp [main,a,b]
      ring
    rw [hid,norm_mul,norm_mul,qc_norm_four,norm_pow]
    exact mul_le_of_le_one_right (mul_nonneg (by norm_num) (sq_nonneg _))
      (PadicInt.norm_le_one _)
  change ‖quadraticCriticalValue a b u R hR-4*e*c0‖≤_
  rw [show quadraticCriticalValue a b u R hR-4*e*c0=
    (quadraticCriticalValue a b u R hR-main)+(main-4*e*c0) by ring]
  exact (IsUltrametricDist.norm_add_le_max _ _).trans (max_le herr hmain)

/-- Correct nonvanishing statement: epsilon must be sufficiently small RELATIVE
TO the first value defect, not merely nonzero or absolutely small. -/
theorem quadraticPerturbation_no_critical (e c0 c1 b1:D) (u:Dˣ)
    (R:Series) (hR:Restricted R) (he:e≠0) (hgap:‖e‖<‖c0‖) (x:D) :
    ¬CriticalZero
      (qeval (quadraticCoreSeries (4*e*c0+16*e^2*c1) (2*e*b1) (u:D) R)) (x:ℚ_[2]) := by
  have hstrict:(1/4:ℝ)*‖e‖^2<‖4*e*c0‖ := by
    rw [norm_mul,norm_mul,qc_norm_four]
    calc
      (1/4:ℝ)*‖e‖^2=((1/4:ℝ)*‖e‖)*‖e‖ := by ring
      _<((1/4:ℝ)*‖e‖)*‖c0‖ :=
        mul_lt_mul_of_pos_left hgap (mul_pos (by norm_num) (norm_pos_iff.mpr he))
  intro hx
  have hz:=(quadraticCriticalValue_zero_iff (4*e*c0+16*e^2*c1)
    (2*e*b1) u R hR).mp ⟨x,hx⟩
  have hh:=(quadraticPerturbation_critical_error e c0 c1 b1 u R hR).trans_lt hstrict
  rw [hz,zero_sub,norm_neg] at hh
  exact (lt_irrefl _) hh

/-- Sharpness control: a genuine double zero can sit exactly on the cubic-error bound.
This is a synthetic polynomial, not an Euler residual. -/
theorem quadraticCritical_sharp_control (c x:D) :
    (x-c)^2*(1+4*x)=c^2+2*(2*c^2-c)*x+(1-8*c)*x^2+4*x^3 := by ring

theorem quadraticCritical_sharp_discriminant (c:D) :
    (1-8*c)*c^2-(2*c^2-c)^2=-4*c^3*(1+c) := by ring

end Komorebi.Euler
