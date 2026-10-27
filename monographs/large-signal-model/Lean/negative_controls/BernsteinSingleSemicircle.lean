import KomorebiLSM.RationalSemicircle
open Komorebi.LSM.LorentzCylinder Komorebi.LSM.RobustOrientedMargin
open Komorebi.LSM.RationalSemicircle

/-- Mass is exactly preserved, but only the right semicircle is cone-positive. -/
noncomputable def rightOnly : State ℂ →L[ℝ] State ℂ :=
  (ContinuousLinearMap.fst ℝ ℝ ℂ).prod
    (Complex.ofRealCLM.comp ((ContinuousLinearMap.fst ℝ ℝ ℂ)-
      Complex.reCLM.comp (ContinuousLinearMap.snd ℝ ℝ ℂ)))

theorem right_mass (z : State ℂ) : (rightOnly z).1=z.1 := rfl

theorem right_orientation (t : ℝ) : orientation rightOnly 0 false t=1+t^2 := by
  simp [orientation,rightOnly,lift,denominator]

theorem right_squared (t : ℝ) : squareGap rightOnly 0 false t=(1-t^2)*(1+3*t^2) := by
  simp [squareGap,orientation,rightOnly,lift,numerator,denominator]
  simp only [← Complex.ofReal_pow,Complex.ofReal_re,Complex.ofReal_im]
  ring

theorem right_tests {t : ℝ} (ht : t∈Set.Icc (-1 : ℝ) 1) :
    0≤orientation rightOnly 0 false t ∧ 0≤squareGap rightOnly 0 false t := by
  have hs : t^2≤1 := by
    have hp := mul_nonneg (sub_nonneg.mpr ht.2) (show (0 : ℝ)≤1+t by linarith [ht.1])
    nlinarith
  constructor
  · rw [right_orientation]
    positivity
  · rw [right_squared]
    exact mul_nonneg (sub_nonneg.mpr hs) (by positivity)

/-- The omitted left endpoint violates the claimed disk margin even with exact mass. -/
example : 0≤slack (rightOnly (1,(-1 : ℂ))) := by
  norm_num [slack,rightOnly]
