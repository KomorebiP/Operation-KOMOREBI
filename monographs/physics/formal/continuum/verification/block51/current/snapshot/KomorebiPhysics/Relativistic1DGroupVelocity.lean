module

public import KomorebiPhysics.Dispersion1D
public import Mathlib.Analysis.SpecialFunctions.Trigonometric.InverseDeriv

/-!
Exact momentum derivative of the principal one-dimensional dispersion branch.
The derivative is stated only away from shell endpoints where arccos is singular.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic1DGroupVelocity

open KomorebiPhysics.Dispersion1D

/-- Momentum derivative of the exact product-cosine shell. -/
theorem hasDerivAt_shell_momentum (m k ε : ℝ) :
    HasDerivAt (fun q => shell m q ε)
      (-(Real.cos (m*ε) * (Real.sin (k*ε) * ε))) k := by
  have hlin := (hasDerivAt_id k).mul (hasDerivAt_const k ε)
  have hcos := hlin.cos
  have hconst := hasDerivAt_const k (Real.cos (m*ε))
  have h := hconst.mul hcos
  change HasDerivAt (fun q : ℝ => Real.cos (m*ε) * Real.cos (q*ε))
    (0 * Real.cos (k*ε) + Real.cos (m*ε) *
      (-Real.sin (k*ε) * (1*ε + k*0))) k at h
  change HasDerivAt (fun q : ℝ => Real.cos (m*ε) * Real.cos (q*ε))
    (-(Real.cos (m*ε) * (Real.sin (k*ε) * ε))) k
  convert h using 1
  ring

/-- Interior shell values are precisely the non-singular points for the arccos derivative. -/
theorem shell_ne_endpoints_of_abs_lt_one {m k ε : ℝ} (h : |shell m k ε| < 1) :
    shell m k ε ≠ -1 ∧ shell m k ε ≠ 1 := by
  constructor <;> intro heq <;> rw [heq] at h <;> norm_num at h

/-- Exact derivative with the square-root denominator supplied directly by arccos differentiation. -/
theorem hasDerivAt_principalFrequency_sqrt (m k ε : ℝ) (hε : ε ≠ 0)
    (hint : |shell m k ε| < 1) :
    HasDerivAt (fun q => principalFrequency m q ε hε)
      (Real.cos (m*ε) * Real.sin (k*ε) /
        Real.sqrt (1 - shell m k ε ^ 2)) k := by
  obtain ⟨hnegn, hone⟩ := shell_ne_endpoints_of_abs_lt_one hint
  have hsquare : shell m k ε ^ 2 < 1 :=
    (sq_lt_one_iff_abs_lt_one (shell m k ε)).2 hint
  have hsqrt : Real.sqrt (1 - shell m k ε ^ 2) ≠ 0 := by
    exact ne_of_gt (Real.sqrt_pos.2 (by linarith))
  have hs := hasDerivAt_shell_momentum m k ε
  have ha := (Real.hasDerivAt_arccos hnegn hone).comp k hs
  have hd := ha.div_const ε
  have hd' : HasDerivAt (fun q => Real.arccos (shell m q ε) / ε)
      (-(1 / Real.sqrt (1 - shell m k ε ^ 2)) *
        (-(Real.cos (m*ε) * (Real.sin (k*ε) * ε))) / ε) k := by
    simpa only [Function.comp_apply] using hd
  have hcoeff :
      (-(1 / Real.sqrt (1 - shell m k ε ^ 2)) *
        (-(Real.cos (m*ε) * (Real.sin (k*ε) * ε))) / ε) =
      (Real.cos (m*ε) * Real.sin (k*ε) /
        Real.sqrt (1 - shell m k ε ^ 2)) := by
    field_simp
  exact hd'.congr_deriv hcoeff

/-- The square-root denominator is the positive principal-branch sine. -/
theorem sqrt_one_sub_shell_sq (m k ε : ℝ) :
    Real.sqrt (1 - shell m k ε ^ 2) = Real.sin (principalPhase m k ε) := by
  rw [← cos_principalPhase m k ε]
  symm
  exact Real.sin_eq_sqrt_one_sub_cos_sq
    (principalPhase_nonneg m k ε) (principalPhase_le_pi m k ε)

/-- Principal-frequency phase cancellation. -/
theorem principalFrequency_mul_spacing (m k ε : ℝ) (hε : ε ≠ 0) :
    principalFrequency m k ε hε * ε = principalPhase m k ε := by
  rw [principalFrequency]
  exact div_mul_cancel₀ _ hε

/-- Equation (8.13): exact group velocity on the non-singular principal branch. -/
theorem hasDerivAt_principalFrequency (m k ε : ℝ) (hε : ε ≠ 0)
    (hint : |shell m k ε| < 1) :
    HasDerivAt (fun q => principalFrequency m q ε hε)
      (Real.cos (m*ε) * Real.sin (k*ε) /
        Real.sin (principalFrequency m k ε hε * ε)) k := by
  have h := hasDerivAt_principalFrequency_sqrt m k ε hε hint
  rw [sqrt_one_sub_shell_sq, ← principalFrequency_mul_spacing m k ε hε] at h
  exact h

/-- The displayed group-velocity denominator is nonzero at every interior shell point. -/
theorem sin_principalFrequency_mul_spacing_ne_zero (m k ε : ℝ) (hε : ε ≠ 0)
    (hint : |shell m k ε| < 1) :
    Real.sin (principalFrequency m k ε hε * ε) ≠ 0 := by
  rw [principalFrequency_mul_spacing, ← sqrt_one_sub_shell_sq]
  have hsquare : shell m k ε ^ 2 < 1 :=
    (sq_lt_one_iff_abs_lt_one (shell m k ε)).2 hint
  have hpos : 0 < 1 - shell m k ε ^ 2 := by linarith
  exact ne_of_gt (Real.sqrt_pos.2 hpos)

/-- Mass sign does not change the exact group velocity. -/
theorem groupVelocity_neg_mass (m k ε : ℝ) (hε : ε ≠ 0) :
    Real.cos ((-m)*ε) * Real.sin (k*ε) /
        Real.sin (principalFrequency (-m) k ε hε * ε) =
      Real.cos (m*ε) * Real.sin (k*ε) /
        Real.sin (principalFrequency m k ε hε * ε) := by
  rw [principalFrequency_neg_mass]
  simp

/-- Momentum reversal flips the exact group velocity. -/
theorem groupVelocity_neg_momentum (m k ε : ℝ) (hε : ε ≠ 0) :
    Real.cos (m*ε) * Real.sin ((-k)*ε) /
        Real.sin (principalFrequency m (-k) ε hε * ε) =
      -(Real.cos (m*ε) * Real.sin (k*ε) /
        Real.sin (principalFrequency m k ε hε * ε)) := by
  rw [principalFrequency_neg_momentum]
  simp only [neg_mul, Real.sin_neg]
  ring

end KomorebiPhysics.Relativistic1DGroupVelocity
