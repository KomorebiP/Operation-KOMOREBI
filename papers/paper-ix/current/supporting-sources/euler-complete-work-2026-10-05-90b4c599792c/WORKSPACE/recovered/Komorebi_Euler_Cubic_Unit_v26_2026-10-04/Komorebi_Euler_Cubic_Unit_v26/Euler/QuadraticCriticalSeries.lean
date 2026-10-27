module
public import Euler.LocalAnalyticTools
public import Euler.PacketDerivatives
public import Euler.CriticalCharts
@[expose] public section
noncomputable section
set_option maxHeartbeats 200000
namespace Komorebi.Euler
open PowerSeries

lemma qc_Xpow_restricted (n : ℕ) : Restricted ((X:Series)^n) := by
  simpa using polynomial_restricted ((Polynomial.X:Polynomial D)^n)

lemma qc_X_restricted : Restricted (X:Series) := by
  simpa using polynomial_restricted (Polynomial.X:Polynomial D)

lemma qc_reval_C (a x : D) : reval (C a:Series) x=a := by
  simpa using reval_polynomial (Polynomial.C a) x

lemma qc_reval_X (x : D) : reval (X:Series) x=x := by
  simpa using reval_polynomial Polynomial.X x

lemma qc_reval_Xpow (n : ℕ) (x : D) : reval ((X:Series)^n) x=x^n := by
  simpa using reval_polynomial ((Polynomial.X:Polynomial D)^n) x

/-- A genuine restricted quadratic core with a coefficientwise 4-divisible cubic tail. -/
def quadraticCoreSeries (a b u : D) (R : Series) : Series :=
  C a+C (2*b)*X+C u*X^2+C (4:D)*X^3*R

/-- Half of the actual analytic derivative, with no division in Z_2. -/
def quadraticCriticalSeries (b u : D) (R : Series) : Series :=
  C b+C u*X+C (2:D)*X^2*(C (3:D)*R+X*hasseSeries 1 R)

lemma quadraticCore_restricted (a b u : D) {R : Series} (hR : Restricted R) :
    Restricted (quadraticCoreSeries a b u R) := by
  unfold quadraticCoreSeries
  exact PowerSeries.isRestricted.add 1
    (PowerSeries.isRestricted.add 1
      (PowerSeries.isRestricted.add 1 (PowerSeries.isRestricted_C 1 a)
        (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) qc_X_restricted))
      (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) (qc_Xpow_restricted 2)))
    (PowerSeries.isRestricted.mul 1
      (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) (qc_Xpow_restricted 3)) hR)

lemma quadraticCritical_restricted (b u : D) {R : Series} (hR : Restricted R) :
    Restricted (quadraticCriticalSeries b u R) := by
  unfold quadraticCriticalSeries
  exact PowerSeries.isRestricted.add 1
    (PowerSeries.isRestricted.add 1 (PowerSeries.isRestricted_C 1 b)
      (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) qc_X_restricted))
    (PowerSeries.isRestricted.mul 1
      (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) (qc_Xpow_restricted 2))
      (PowerSeries.isRestricted.add 1
        (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) hR)
        (PowerSeries.isRestricted.mul 1 qc_X_restricted (restricted_hasseSeries hR 1))))

lemma quadraticCritical_red (b u : D) (hu : red u=1) (R : Series) :
    PowerSeries.map red (quadraticCriticalSeries b u R)=X+C (red b) := by
  simp only [quadraticCriticalSeries,map_add,map_mul,map_C,map_X,map_pow,
    red_two,map_zero,zero_mul,add_zero,hu,map_one,one_mul]
  ring

lemma quadraticCore_reval (a b u : D) {R : Series} (hR : Restricted R) (x : D) :
    reval (quadraticCoreSeries a b u R) x =
      a+2*b*x+u*x^2+4*x^3*reval R x := by
  let p : Polynomial D := Polynomial.C a+Polynomial.C (2*b)*Polynomial.X+
    Polynomial.C u*Polynomial.X^2
  have hp : (p:Series)=C a+C (2*b)*X+C u*X^2 := by simp [p]
  have hprod : Restricted ((X:Series)^3*R) :=
    PowerSeries.isRestricted.mul 1 (qc_Xpow_restricted 3) hR
  have he : quadraticCoreSeries a b u R=(p:Series)+C (4:D)*((X:Series)^3*R) := by
    rw [hp]; simp only [quadraticCoreSeries,mul_assoc]
  rw [he,reval_add (polynomial_restricted p)
    (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) hprod),
    reval_polynomial,reval_C_mul hprod,reval_mul (qc_Xpow_restricted 3) hR,qc_reval_Xpow]
  simp only [p,Polynomial.eval_add,Polynomial.eval_mul,Polynomial.eval_C,
    Polynomial.eval_X,Polynomial.eval_pow]
  ring

lemma quadraticCritical_reval (b u : D) {R : Series} (hR : Restricted R) (x : D) :
    reval (quadraticCriticalSeries b u R) x =
      b+u*x+2*x^2*(3*reval R x+x*rjet 1 R x) := by
  let p : Polynomial D := Polynomial.C b+Polynomial.C u*Polynomial.X
  let S : Series := C (3:D)*R+X*hasseSeries 1 R
  have hp : (p:Series)=C b+C u*X := by simp [p]
  have hR' := restricted_hasseSeries hR 1
  have hS : Restricted S := PowerSeries.isRestricted.add 1
    (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) hR)
    (PowerSeries.isRestricted.mul 1 qc_X_restricted hR')
  have hprod := PowerSeries.isRestricted.mul 1 (qc_Xpow_restricted 2) hS
  have he : quadraticCriticalSeries b u R=(p:Series)+C (2:D)*((X:Series)^2*S) := by
    rw [hp]; simp only [quadraticCriticalSeries,S,mul_assoc]
  rw [he,reval_add (polynomial_restricted p)
    (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) hprod),
    reval_polynomial,reval_C_mul hprod,reval_mul (qc_Xpow_restricted 2) hS,qc_reval_Xpow]
  have heS : reval S x=3*reval R x+x*rjet 1 R x := by
    dsimp only [S]
    rw [reval_add (PowerSeries.isRestricted.mul 1 (PowerSeries.isRestricted_C 1 _) hR)
      (PowerSeries.isRestricted.mul 1 qc_X_restricted hR'), reval_C_mul hR,reval_X_mul hR']
    rfl
  rw [heS]
  simp only [p,Polynomial.eval_add,Polynomial.eval_mul,Polynomial.eval_C,Polynomial.eval_X]
  ring

lemma quadraticCore_rjet_one (a b u : D) {R : Series} (hR : Restricted R) (x : D) :
    rjet 1 (quadraticCoreSeries a b u R) x=
      2*reval (quadraticCriticalSeries b u R) x := by
  have hid : hasseSeries 1 (quadraticCoreSeries a b u R) =
      C (2:D)*quadraticCriticalSeries b u R := by
    rw [hasseSeries_one_eq_derivative]
    simp only [quadraticCoreSeries,quadraticCriticalSeries,map_add,
      Derivation.leibniz,smul_eq_mul,PowerSeries.derivative_C,PowerSeries.derivative_X,
      PowerSeries.derivative_pow,hasseSeries_one_eq_derivative]
    norm_num
    simp only [map_ofNat]
    ring
  unfold rjet
  rw [hid,reval_C_mul (quadraticCritical_restricted b u hR)]

/-- Unique actual critical point, including its exact distance from zero. -/
theorem quadraticCore_unique_critical (a b u : D) {R : Series} (hR : Restricted R)
    (hu : red u=1) :
    ∃ c : D,
      (∀ x : D, deriv (qeval (quadraticCoreSeries a b u R)) (x:ℚ_[2])=0 ↔ x=c) ∧
      ‖c‖=‖b‖ ∧
      reval (quadraticCriticalSeries b u R) c=0 := by
  obtain ⟨c,hc,_,huniq,hdist⟩ := restricted_affine_atlas
    (quadraticCritical_restricted b u hR) (red b) (quadraticCritical_red b u hu R)
  refine ⟨c,?_,?_,hc⟩
  · intro x
    rw [deriv_qeval (quadraticCore_restricted a b u hR),quadraticCore_rjet_one a b u hR]
    simp only [PadicInt.coe_mul, mul_eq_zero, show ((2:D):ℚ_[2])≠0 from by norm_num,
      false_or, PadicInt.coe_eq_zero,huniq]
  · have h := hdist 0
    rw [quadraticCritical_reval b u hR] at h
    simpa only [mul_zero,zero_pow (by decide : 2≠0),zero_mul,add_zero,zero_sub,norm_neg] using h.symm

end Komorebi.Euler
