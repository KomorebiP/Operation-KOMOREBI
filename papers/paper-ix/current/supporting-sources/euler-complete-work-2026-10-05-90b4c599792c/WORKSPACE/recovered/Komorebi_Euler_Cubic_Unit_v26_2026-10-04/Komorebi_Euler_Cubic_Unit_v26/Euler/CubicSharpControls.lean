module
public import Euler.CubicCriticalValues
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

lemma cubic_zero_restricted : Restricted (0:Series) := by
  simpa using polynomial_restricted (0:Polynomial D)

/-- Synthetic sharp control, not an Euler-family assertion. -/
theorem cubicDoubleControl_factor (s x:D) :
    reval (cubicCoreSeries (2*s^3) (-3*s^2) 0 1 0) x=(x-s)^2*(x+2*s) := by
  rw [cubicCore_reval _ _ _ _ cubic_zero_restricted]
  simp [reval]
  ring

theorem cubicDoubleControl_critical (s:D) :
    CriticalZero (qeval (cubicCoreSeries (2*s^3) (-3*s^2) 0 1 0)) (s:ℚ_[2]) := by
  constructor
  · rw [←coe_reval (cubicCore_restricted _ _ _ _ cubic_zero_restricted),cubicDoubleControl_factor]
    simp
  · rw [deriv_qeval (cubicCore_restricted _ _ _ _ cubic_zero_restricted),cubicCore_rjet_one _ _ _ _ cubic_zero_restricted]
    norm_num [rjet,reval,hasseSeries]

/-- The scale-equality boundary can contain genuine double roots. -/
theorem cubicDoubleControl_discriminant (s:D) :
    4*(-3*s^2)^3+27*(2*s^3)^2=0 := by ring

/-- Scale equality is not sufficient: the corresponding reduced polynomial
obstruction for X^3+3X+2 is nonzero. -/
theorem cubicEqualScale_nondegenerate : (4*(3:D)^3+27*(2:D)^2)≠0 := by
  norm_num

end Komorebi.Euler
