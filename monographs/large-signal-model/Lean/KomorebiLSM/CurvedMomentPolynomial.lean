import KomorebiLSM.CurvedMomentInstrument
import KomorebiLSM.PolynomialGram
import Mathlib.Tactic

/-! Explicit degree-four coefficient matrices and reference-weighted moments. -/
set_option autoImplicit false
namespace Komorebi.LSM.CurvedMoment
open MeasureTheory
open scoped Matrix BigOperators
noncomputable section

def coefficientMatrix (a b : ℝ) : Fin 5 → Matrix (Fin 3) (Fin 3) ℝ :=
  ![!![1,0,-b/2;0,0,0;0,0,0],
    !![0,a,0;1,0,-b/2;0,0,0],
    !![0,0,3*b/2;0,a,0;1,0,-b/2],
    !![0,0,0;0,0,3*b/2;0,a,0],
    !![0,0,0;0,0,0;0,0,3*b/2]]

def coefficientOperator (a b : ℝ) (k : Fin 5) : State →L[ℝ] State :=
  (coefficientMatrix a b k).mulVecLin.toContinuousLinearMap

theorem branch_polynomial (a b u : ℝ) :
    PolynomialGram.operatorPolynomial (coefficientOperator a b) u=branch a b u := by
  ext z i
  fin_cases i <;>
    norm_num [PolynomialGram.operatorPolynomial,coefficientOperator,coefficientMatrix,
      Fin.sum_univ_succ,Matrix.mulVec,dotProduct,branch_apply,likelihood,legendre,curve] <;> ring

namespace Reference
variable {μ : Measure ℝ} (R : Reference μ)
include R

theorem integral_polynomial (c : Fin 5 → ℝ) :
    (∫ u,∑ k : Fin 5,c k*u^(k:ℕ)∂μ)=c 0+c 2/3+c 4/5 := by
  let := R.probability
  rw [integral_finsetSum (f:=fun (k:Fin 5) u => c k*u^(k:ℕ)) _ (fun k _ =>
    (R.continuous_integrable (f:=fun u : ℝ => u^(k:ℕ)) (by fun_prop)).const_mul (c k))]
  simp only [integral_const_mul]
  norm_num [Fin.sum_univ_succ,R.first,R.second,R.third,R.fourth]
  change c 0+(c 2*(1/3)+c 4*(1/5))=c 0+c 2/3+c 4/5
  ring

theorem integral_signal_likelihood (a b : ℝ) (z : State) :
    (∫ u,u*likelihood a b u z∂μ)=a*z 1/3 := by
  have he : (fun u => u*likelihood a b u z)=
      (fun u => ∑ k : Fin 5,(![0,z 0-b*z 2/2,a*z 1,3*b*z 2/2,0] k)*u^(k:ℕ)) := by
    funext u
    norm_num [Fin.sum_univ_succ,likelihood,legendre]
    ring
  rw [he,R.integral_polynomial]
  change 0+(a*z 1)/3+0/5=a*z 1/3
  ring

theorem integral_legendre_likelihood (a b : ℝ) (z : State) :
    (∫ u,legendre u*likelihood a b u z∂μ)=b*z 2/5 := by
  have he : (fun u => legendre u*likelihood a b u z)=
      (fun u => ∑ k : Fin 5,(![-z 0/2+b*z 2/4,-a*z 1/2,
        3*z 0/2-3*b*z 2/2,3*a*z 1/2,9*b*z 2/4] k)*u^(k:ℕ)) := by
    funext u
    norm_num [Fin.sum_univ_succ,likelihood,legendre]
    ring
  rw [he,R.integral_polynomial]
  change (-z 0/2+b*z 2/4)+(3*z 0/2-3*b*z 2/2)/3+(9*b*z 2/4)/5=b*z 2/5
  ring

end Reference
end
end Komorebi.LSM.CurvedMoment
