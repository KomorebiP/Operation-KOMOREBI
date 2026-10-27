module
public import Euler.CubicCriticalSeries
public import Euler.SecondOrderRemainder
@[expose] public section
noncomputable section
set_option maxHeartbeats 700000
namespace Komorebi.Euler
open PowerSeries

lemma cubic_triple_isUnit (u:Dˣ) : IsUnit (3*(u:D)) := by
  apply PadicInt.isUnit_iff.mpr
  apply res_nonzero_norm_one
  simp only [res_eq_red,map_mul,qc_unit_red,mul_one]
  rw [show (3:D)=(2:D)+1 by norm_num,map_add,red_two,map_one]
  decide

def cubicSlopeUnit (u:Dˣ) : Dˣ := (cubic_triple_isUnit u).unit

lemma cubicSlopeUnit_val (u:Dˣ) : (cubicSlopeUnit u:D)=3*(u:D) :=
  (cubic_triple_isUnit u).unit_spec

def cubicInflectionPoint (c:D) (u:Dˣ) (R:Series) (hR:Restricted R) : D :=
  quadraticCriticalPoint c (cubicSlopeUnit u) (cubicDerivativeTail R)
    (cubicDerivativeTail_restricted hR)

lemma cubicCore_second_deriv (a b c u:D) {R:Series} (hR:Restricted R) (x:D) :
    deriv (deriv (qeval (cubicCoreSeries a b c u R))) (x:ℚ_[2])=
      deriv (qeval (quadraticCoreSeries b c (3*u) (cubicDerivativeTail R))) (x:ℚ_[2]) := by
  have h := deriv_qeval_eventually (cubicCore_restricted a b c u hR) x
  rw [cubicCore_hasse_one] at h
  exact h.deriv_eq

/-- The inflection point of the ACTUAL infinite cubic is constructed uniquely. -/
theorem cubicInflection_unique (a b c:D) (u:Dˣ) (R:Series) (hR:Restricted R) (x:D) :
    deriv (deriv (qeval (cubicCoreSeries a b c (u:D) R))) (x:ℚ_[2])=0 ↔
      x=cubicInflectionPoint c u R hR := by
  rw [cubicCore_second_deriv a b c (u:D) hR,←cubicSlopeUnit_val u]
  exact quadraticCriticalPoint_unique b c (cubicSlopeUnit u)
    (cubicDerivativeTail R) (cubicDerivativeTail_restricted hR) x

lemma cubicInflection_norm (c:D) (u:Dˣ) (R:Series) (hR:Restricted R) :
    ‖cubicInflectionPoint c u R hR‖=‖c‖ :=
  quadraticCriticalPoint_norm c (cubicSlopeUnit u) (cubicDerivativeTail R)
    (cubicDerivativeTail_restricted hR)

lemma cubicInflection_rjet_two (a b c:D) (u:Dˣ) (R:Series) (hR:Restricted R) :
    rjet 2 (cubicCoreSeries a b c (u:D) R) (cubicInflectionPoint c u R hR)=0 := by
  have h := (cubicInflection_unique a b c u R hR _).mpr rfl
  rw [second_deriv_qeval (cubicCore_restricted a b c (u:D) hR)] at h
  exact PadicInt.coe_eq_zero.mp ((mul_eq_zero.mp h).resolve_left (by norm_num))

/-- The derivative's distance from its inflection value is an EXACT square norm. -/
theorem cubicInflection_slope_distance (a b c:D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (x:D) :
    ‖rjet 1 (cubicCoreSeries a b c (u:D) R) x-
      rjet 1 (cubicCoreSeries a b c (u:D) R) (cubicInflectionPoint c u R hR)‖=
      ‖x-cubicInflectionPoint c u R hR‖^2 := by
  simp only [rjet,cubicCore_hasse_one,←cubicSlopeUnit_val u]
  exact quadraticStationary_value_distance b c (cubicSlopeUnit u)
    (cubicDerivativeTail R) (cubicDerivativeTail_restricted hR) x

lemma rjet_add_value (k:ℕ) {f g:Series} (hf:Restricted f) (hg:Restricted g) (x:D) :
    rjet k (f+g) x=rjet k f x+rjet k g x := by
  have he : hasseSeries k (f+g)=hasseSeries k f+hasseSeries k g := by
    ext n
    simp only [coeff_hasseSeries,map_add,mul_add]
  unfold rjet
  rw [he,reval_add (restricted_hasseSeries hf k) (restricted_hasseSeries hg k)]

lemma rjet_polynomial_order (k:ℕ) (p:Polynomial D) (x:D) :
    rjet k (p:Series) x=(Polynomial.hasseDeriv k p).eval x := by
  have he : hasseSeries k (p:Series)=(Polynomial.hasseDeriv k p:Polynomial D) := by
    ext n
    simp [coeff_hasseSeries,Polynomial.hasseDeriv_coeff]
  unfold rjet
  rw [he,reval_polynomial]

lemma cubicCore_rjet_two (a b c u:D) {R:Series} (hR:Restricted R) (x:D) :
    rjet 2 (cubicCoreSeries a b c u R) x=c+3*u*x+4*rjet 2 ((X:Series)^4*R) x := by
  let p : Polynomial D := Polynomial.C a+Polynomial.C b*Polynomial.X+
    Polynomial.C c*Polynomial.X^2+Polynomial.C u*Polynomial.X^3
  have he : cubicCoreSeries a b c u R=(p:Series)+C (4:D)*((X:Series)^4*R) := by
    simp only [p,cubicCoreSeries,Polynomial.coe_add,Polynomial.coe_mul,
      Polynomial.coe_C,Polynomial.coe_X,Polynomial.coe_pow,mul_assoc]
  rw [he,rjet_add_value 2 (polynomial_restricted p)
    (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) (cubicTail_restricted hR)),
    rjet_polynomial_order,rjet_C_mul (cubicTail_restricted hR)]
  have hp : Polynomial.hasseDeriv 2 p=Polynomial.C c+Polynomial.C (3*u)*Polynomial.X := by
    ext n
    rcases n with _ | _ | n
    · norm_num [p,Polynomial.hasseDeriv_coeff]
    · norm_num [p,Polynomial.hasseDeriv_coeff]
    · simp [p,Polynomial.hasseDeriv_coeff]
  rw [hp]
  simp

end Komorebi.Euler
