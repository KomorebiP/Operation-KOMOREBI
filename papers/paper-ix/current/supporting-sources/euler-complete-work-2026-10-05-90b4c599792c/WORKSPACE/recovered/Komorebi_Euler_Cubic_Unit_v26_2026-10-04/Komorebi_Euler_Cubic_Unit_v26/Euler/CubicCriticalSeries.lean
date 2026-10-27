module
public import Euler.StationaryValuePrecision
public import Euler.TrapezoidRemainder
@[expose] public section
noncomputable section
set_option maxHeartbeats 600000
namespace Komorebi.Euler
open PowerSeries

def cubicCoreSeries (a b c u : D) (R : Series) : Series :=
  C a+C b*X+C c*X^2+C u*X^3+C (4:D)*X^4*R

def cubicDerivativeTail (R : Series) : Series := C (4:D)*R+X*hasseSeries 1 R

lemma cubicTail_restricted {R : Series} (hR : Restricted R) :
    Restricted ((X:Series)^4*R) :=
  PowerSeries.isRestricted.mul 1 (qc_Xpow_restricted 4) hR

lemma cubicDerivativeTail_restricted {R : Series} (hR : Restricted R) :
    Restricted (cubicDerivativeTail R) := by
  exact PowerSeries.isRestricted.add 1
    (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) hR)
    (PowerSeries.isRestricted.mul 1 qc_X_restricted (restricted_hasseSeries hR 1))

lemma cubicCore_restricted (a b c u : D) {R : Series} (hR : Restricted R) :
    Restricted (cubicCoreSeries a b c u R) := by
  unfold cubicCoreSeries
  exact PowerSeries.isRestricted.add 1
    (PowerSeries.isRestricted.add 1
      (PowerSeries.isRestricted.add 1
        (PowerSeries.isRestricted.add 1 (PowerSeries.isRestricted_C 1 a)
          (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) qc_X_restricted))
        (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) (qc_Xpow_restricted 2)))
      (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) (qc_Xpow_restricted 3)))
    (PowerSeries.isRestricted.mul 1
      (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) (qc_Xpow_restricted 4)) hR)

lemma cubicCore_reval (a b c u : D) {R : Series} (hR : Restricted R) (x : D) :
    reval (cubicCoreSeries a b c u R) x =
      a+b*x+c*x^2+u*x^3+4*reval ((X:Series)^4*R) x := by
  let p : Polynomial D := Polynomial.C a+Polynomial.C b*Polynomial.X+
    Polynomial.C c*Polynomial.X^2+Polynomial.C u*Polynomial.X^3
  have he : cubicCoreSeries a b c u R=(p:Series)+C (4:D)*((X:Series)^4*R) := by
    simp only [p,cubicCoreSeries,Polynomial.coe_add,Polynomial.coe_mul,
      Polynomial.coe_C,Polynomial.coe_X,Polynomial.coe_pow,mul_assoc]
  rw [he,reval_add (polynomial_restricted p)
    (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) (cubicTail_restricted hR)),
    reval_polynomial,reval_C_mul (cubicTail_restricted hR)]
  simp [p]

/-- The genuine derivative is itself in the quadratic class from v24. -/
lemma cubicCore_hasse_one (a b c u : D) (R : Series) :
    hasseSeries 1 (cubicCoreSeries a b c u R) =
      quadraticCoreSeries b c (3*u) (cubicDerivativeTail R) := by
  simp only [hasseSeries_one_eq_derivative,cubicCoreSeries,quadraticCoreSeries,
    cubicDerivativeTail,map_add,Derivation.leibniz,smul_eq_mul,
    PowerSeries.derivative_C,PowerSeries.derivative_X,PowerSeries.derivative_pow]
  norm_num
  simp only [map_ofNat]
  ring

lemma cubicCore_rjet_one (a b c u : D) {R : Series} (hR : Restricted R) (x : D) :
    rjet 1 (cubicCoreSeries a b c u R) x =
      b+2*c*x+3*u*x^2+4*rjet 1 ((X:Series)^4*R) x := by
  let p : Polynomial D := Polynomial.C a+Polynomial.C b*Polynomial.X+
    Polynomial.C c*Polynomial.X^2+Polynomial.C u*Polynomial.X^3
  have he : hasseSeries 1 (cubicCoreSeries a b c u R)=
      ((Polynomial.derivative p):Series)+C (4:D)*hasseSeries 1 ((X:Series)^4*R) := by
    simp only [hasseSeries_one_eq_derivative,cubicCoreSeries,p,map_add,
      Derivation.leibniz,smul_eq_mul,PowerSeries.derivative_C,
      PowerSeries.derivative_X,PowerSeries.derivative_pow]
    norm_num
    simp only [map_ofNat]
    ring
  unfold rjet
  rw [he,reval_add (polynomial_restricted _)
    (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _)
      (restricted_hasseSeries (cubicTail_restricted hR) 1)),
    reval_polynomial,reval_C_mul (restricted_hasseSeries (cubicTail_restricted hR) 1)]
  norm_num [p]
  ring

lemma cubicCore_deriv (a b c u : D) {R : Series} (hR : Restricted R) (x : D) :
    deriv (qeval (cubicCoreSeries a b c u R)) (x:ℚ_[2])=
      (reval (quadraticCoreSeries b c (3*u) (cubicDerivativeTail R)) x:ℚ_[2]) := by
  rw [deriv_qeval (cubicCore_restricted a b c u hR)]
  simp only [rjet,cubicCore_hasse_one]

/-- Exact all-point cubic trapezoid invariant, including the infinite tail. -/
theorem cubicCore_trapezoid_norm (a b c : D) (u:Dˣ) {R : Series}
    (hR : Restricted R) (x y : D) :
    ‖2*(reval (cubicCoreSeries a b c (u:D) R) y-
      reval (cubicCoreSeries a b c (u:D) R) x)-
      (y-x)*(rjet 1 (cubicCoreSeries a b c (u:D) R) x+
        rjet 1 (cubicCoreSeries a b c (u:D) R) y)‖=‖y-x‖^3 := by
  let T : Series := (X:Series)^4*R
  let e : D := 2*(reval T y-reval T x)-(y-x)*(rjet 1 T x+rjet 1 T y)
  have he : ‖e‖≤‖y-x‖^3 := reval_trapezoid_error (cubicTail_restricted hR) x y
  rw [cubicCore_reval a b c (u:D) hR,cubicCore_reval a b c (u:D) hR,
    cubicCore_rjet_one a b c (u:D) hR,cubicCore_rjet_one a b c (u:D) hR]
  have hi : 2*((a+b*y+c*y^2+(u:D)*y^3+4*reval T y)-
      (a+b*x+c*x^2+(u:D)*x^3+4*reval T x))-
      (y-x)*((b+2*c*x+3*(u:D)*x^2+4*rjet 1 T x)+
      (b+2*c*y+3*(u:D)*y^2+4*rjet 1 T y))=
      -(u:D)*(y-x)^3+4*e := by dsimp only [e];ring
  change ‖2*((a+b*y+c*y^2+(u:D)*y^3+4*reval T y)-
      (a+b*x+c*x^2+(u:D)*x^3+4*reval T x))-
      (y-x)*((b+2*c*x+3*(u:D)*x^2+4*rjet 1 T x)+
      (b+2*c*y+3*(u:D)*y^2+4*rjet 1 T y))‖=_
  rw [hi]
  by_cases hxy:y=x
  · subst y; simp [e]
  have hp : 0<‖y-x‖^3 := pow_pos (norm_pos_iff.mpr (sub_ne_zero.mpr hxy)) _
  have hlt : ‖(4:D)*e‖<‖-(u:D)*(y-x)^3‖ := by
    rw [norm_mul,qc_norm_four,norm_mul,norm_neg,PadicInt.norm_units,one_mul,norm_pow]
    exact (mul_le_mul_of_nonneg_left he (by norm_num : (0:ℝ)≤1/4)).trans_lt (by nlinarith)
  have hn := PadicInt.norm_eq_of_norm_add_lt_right
    (z1:=-(u:D)*(y-x)^3+4*e) (z2:=(u:D)*(y-x)^3) (by
      rw [show -(u:D)*(y-x)^3+4*e+(u:D)*(y-x)^3=4*e by ring]
      simpa only [neg_mul,norm_neg] using hlt)
  simpa only [norm_mul,PadicInt.norm_units,one_mul,norm_pow] using hn

/-- Distinct critical points have distinct critical values, with an EXACT gap. -/
theorem cubicCore_critical_value_separation (a b c : D) (u:Dˣ) {R:Series}
    (hR:Restricted R) (x y:D)
    (hx:deriv (qeval (cubicCoreSeries a b c (u:D) R)) (x:ℚ_[2])=0)
    (hy:deriv (qeval (cubicCoreSeries a b c (u:D) R)) (y:ℚ_[2])=0) :
    ‖reval (cubicCoreSeries a b c (u:D) R) y-
      reval (cubicCoreSeries a b c (u:D) R) x‖=2*‖y-x‖^3 := by
  rw [deriv_qeval (cubicCore_restricted a b c (u:D) hR),PadicInt.coe_eq_zero] at hx hy
  have h := cubicCore_trapezoid_norm a b c u hR x y
  rw [hx,hy,add_zero,mul_zero,sub_zero,norm_mul,norm_two] at h
  linarith

/-- At most one repeated zero is possible in the entire cubic-core disc. -/
theorem cubicCore_critical_zero_unique (a b c : D) (u:Dˣ) {R:Series}
    (hR:Restricted R) (x y:D)
    (hx:CriticalZero (qeval (cubicCoreSeries a b c (u:D) R)) (x:ℚ_[2]))
    (hy:CriticalZero (qeval (cubicCoreSeries a b c (u:D) R)) (y:ℚ_[2])) : x=y := by
  have h := cubicCore_critical_value_separation a b c u hR x y hx.2 hy.2
  have hx0 : reval (cubicCoreSeries a b c (u:D) R) x=0 := by
    apply PadicInt.coe_eq_zero.mp
    simpa only [coe_reval (cubicCore_restricted a b c (u:D) hR)] using hx.1
  have hy0 : reval (cubicCoreSeries a b c (u:D) R) y=0 := by
    apply PadicInt.coe_eq_zero.mp
    simpa only [coe_reval (cubicCore_restricted a b c (u:D) hR)] using hy.1
  rw [hx0,hy0,sub_self,norm_zero] at h
  have hz3:‖y-x‖^3=0 := by linarith
  have hz:‖y-x‖=0 := (pow_eq_zero_iff (by decide : 3≠0)).mp hz3
  exact (sub_eq_zero.mp (norm_eq_zero.mp hz)).symm

end Komorebi.Euler
