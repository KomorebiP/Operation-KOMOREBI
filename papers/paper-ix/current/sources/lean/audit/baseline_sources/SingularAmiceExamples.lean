module
public import SingularRatioAmice
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.SingularAmiceExamples
open PowerSeries SectionLogBridge WeightedAmice SingularNormalizedSection SingularRatioAmice

/-- Removing the forced zero really is necessary: a positive section is not a unit. -/
theorem positive_section_zero_constant (N c : ℕ) (hc : 0<c) :
    constantCoeff (ExponentialSection.originalSection N c)=0 := by
  simp [ExponentialSection.originalSection, Nat.ne_of_lt hc]

/-- The normalized object, in contrast, has a genuine formal-series inverse. -/
theorem normalized_section_isUnit (p : ℕ) [Fact p.Prime] (N : ℕ) (hN : N≠0) (c : ℕ) :
    IsUnit (normalizedUnit p N hN c) := by
  rw [PowerSeries.isUnit_iff_constantCoeff, normalized_constant]
  exact isUnit_one

/-- Concrete singular address R_3 for N=6 is included by the universal theorem. -/
theorem p3_singular_ratio_weighted :
    Weighted 3 (ratioPullback 3 6 (by decide) 2) := by
  exact singular_ratio_weighted 3 6 (by decide) (by decide) 1 2 (by decide) (by decide)

theorem p3_singular_ratio_constant :
    constantCoeff (rationalRatioPullback 6 (by decide) 2)=3 := by
  norm_num [rational_pullback_constant]

/-- These coefficients are derived from the actual logarithmic section differential recurrence. -/
theorem section3_first (r : ZMod 3) :
    coeff 1 (sectionPullback 3 r) = if r=1 then 1 else 0 := by
  have h := pullback_recurrence 3 0 r
  simp only [pullback_zero, Nat.cast_zero, zero_add, one_mul, zero_mul, sub_zero] at h
  have he : r-1=0 ↔ r=1 := sub_eq_zero
  simpa only [he] using h

theorem section3_second_zero : coeff 2 (sectionPullback 3 0)=0 := by
  have h := pullback_recurrence 3 1 (0:ZMod 3)
  norm_num [section3_first, show (-1:ZMod 3) ≠ 1 by decide] at h ⊢
  linarith

theorem section3_second_two : coeff 2 (sectionPullback 3 2)=1/2 := by
  have h := pullback_recurrence 3 1 (2:ZMod 3)
  norm_num [section3_first, show (2:ZMod 3) ≠ 1 by decide] at h ⊢
  linarith

theorem section3_first_nonconstant : coeff 3 (sectionPullback 3 0)=1/6 := by
  have h := pullback_recurrence 3 2 (0:ZMod 3)
  have hr : (0:ZMod 3)-1=2 := by decide
  rw [hr, section3_second_two, section3_second_zero] at h
  norm_num at h ⊢
  linarith

/-- Weighted membership must not be confused with ordinary coefficient integrality. -/
theorem section3_coefficient_valuation :
    padicValRat 3 (coeff 3 (sectionPullback 3 0)) = -1 := by
  rw [section3_first_nonconstant]
  norm_num [padicValRat]
  rw [show (6:ℕ)=3*2 by decide, padicValNat.mul (by decide : (3:ℕ)≠0)
    (by decide : (2:ℕ)≠0)]
  norm_num [padicValNat.eq_zero_of_not_dvd]

/-- The weighted lower bound at this degree is attained exactly. -/
theorem section3_bound_sharp :
    padicValRat 3 (coeff 3 (sectionPullback 3 0)) = -((3/3:ℕ):ℤ) := by
  rw [section3_coefficient_valuation]
  norm_num

end KomorebiPaperIX.SingularAmiceExamples
