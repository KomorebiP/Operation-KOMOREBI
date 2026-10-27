module
public import Euler.CubicUnitObstruction
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

/-- A nonzero jet discriminant is not the same as a nonzero exact analytic discriminant. -/
lemma cubicQuartic_planted_factor (h x:D) :
    2*h^3+12*h^4+(-3*h^2-16*h^3)*x+x^3+4*x^4 =
      (x-h)^2*(4*x^2+(1+8*h)*x+2*h+12*h^2) := by ring

lemma cubicQuartic_planted_jets (h:D) :
    (2*h^3+12*h^4+(-3*h^2-16*h^3)*h+h^3+4*h^4=0) ∧
      ((-3*h^2-16*h^3)+3*h^2+16*h^3=0) := by constructor <;> ring

lemma cubicQuartic_jet_discriminant (h:D) :
    4*(-3*h^2-16*h^3)^3+27*(2*h^3+12*h^4)^2 =
      -16*h^7*(27+333*h+1024*h^2) := by ring

/-- Genuine analytic critical zero for an infinite-core type (here the tail is constant). -/
theorem cubicQuartic_actual_critical :
    CriticalZero (qeval (cubicCoreSeries 208 (-140) 0 1 (C (1:D)))) ((2:D):ℚ_[2]) := by
  have hR:Restricted (C (1:D)):=PowerSeries.isRestricted_C 1 _
  have hv:reval (cubicCoreSeries 208 (-140) 0 1 (C (1:D))) (2:D)=0 := by
    rw [cubicCore_reval 208 (-140) 0 1 hR]
    norm_num [reval,coeff_mul,coeff_X_pow,coeff_C]
  have hd:rjet 1 (cubicCoreSeries 208 (-140) 0 1 (C (1:D))) (2:D)=0 := by
    rw [cubicCore_rjet_one 208 (-140) 0 1 hR]
    have he:(X:Series)^4*C (1:D)=((Polynomial.X^4:Polynomial D):Series) := by simp
    rw [he,rjet_polynomial_order]
    norm_num [Polynomial.hasseDeriv_one]
  constructor
  · have h:=congrArg (fun z:D=>(z:ℚ_[2])) hv
    rw [coe_reval (cubicCore_restricted 208 (-140) 0 1 hR)] at h
    simpa only [PadicInt.coe_zero] using h
  · have h:=deriv_qeval (cubicCore_restricted 208 (-140) 0 1 hR) (2:D)
    rw [hd] at h
    simpa only [PadicInt.coe_zero] using h

end Komorebi.Euler
