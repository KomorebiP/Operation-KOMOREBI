import KomorebiLSM.RationalSemicircle
open Komorebi.LSM.LorentzCylinder Komorebi.LSM.RobustOrientedMargin
open Komorebi.LSM.RationalSemicircle
noncomputable def reversed : State ℂ →L[ℝ] State ℂ := -ContinuousLinearMap.id ℝ (State ℂ)

/-- Reversed mass satisfies the squared test on both literal charts. -/
theorem reversed_squared (left : Bool) (t : ℝ) : squareGap reversed 0 left t=0 := by
  cases left <;> simp [squareGap,orientation,reversed,lift,numerator,denominator] <;> ring

/-- Omitting orientation would incorrectly accept this actual negative slack. -/
example : 0≤slack (reversed (1,(1 : ℂ))) := by
  norm_num [slack,reversed]
