module

public import KomorebiPhysics.Dispersion1D

/-!
Spacing-parity facts for the principal inverse-cosine branch.

The lattice spacing is physically positive in the small-spacing expansion.  This
module records why that restriction matters: the shell and principal phase are
even in the spacing, whereas dividing the phase by the spacing makes the
principal frequency odd on the punctured line.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic1DSpacingParity

open KomorebiPhysics.Dispersion1D

/-- The exact product-cosine shell is even in the lattice spacing. -/
theorem shell_neg_spacing (m k ε : ℝ) :
    shell m k (-ε) = shell m k ε := by
  simp [shell]

/-- The principal inverse-cosine phase is even in the lattice spacing. -/
theorem principalPhase_neg_spacing (m k ε : ℝ) :
    principalPhase m k (-ε) = principalPhase m k ε := by
  simp [principalPhase, shell_neg_spacing]

/-- On nonzero spacings the principal frequency is odd in the spacing. -/
theorem principalFrequency_neg_spacing (m k ε : ℝ) (hε : ε ≠ 0) :
    principalFrequency m k (-ε) (neg_ne_zero.mpr hε) =
      -principalFrequency m k ε hε := by
  rw [principalFrequency, principalFrequency, principalPhase_neg_spacing]
  field_simp

/-- For negative spacing the principal frequency is nonpositive. -/
theorem principalFrequency_nonpos_of_neg (m k ε : ℝ) (hε : ε < 0) :
    principalFrequency m k ε (ne_of_lt hε) ≤ 0 := by
  rw [principalFrequency]
  exact div_nonpos_of_nonneg_of_nonpos (principalPhase_nonneg m k ε) hε.le

/-- A total extension used only to state exact parity; it does not assign the
continuum energy at zero. -/
def totalFrequency (m k ε : ℝ) : ℝ :=
  if hε : ε = 0 then 0 else principalFrequency m k ε hε

@[simp] theorem totalFrequency_zero (m k : ℝ) : totalFrequency m k 0 = 0 := by
  simp [totalFrequency]

/-- Away from zero the total extension is the already checked principal frequency. -/
theorem totalFrequency_of_ne (m k ε : ℝ) (hε : ε ≠ 0) :
    totalFrequency m k ε = principalFrequency m k ε hε := by
  simp [totalFrequency, hε]

/-- The totalized principal branch is exactly odd in the spacing. -/
theorem totalFrequency_neg (m k ε : ℝ) :
    totalFrequency m k (-ε) = -totalFrequency m k ε := by
  by_cases hε : ε = 0
  · subst ε
    simp
  · rw [totalFrequency_of_ne m k (-ε) (neg_ne_zero.mpr hε),
        totalFrequency_of_ne m k ε hε,
        principalFrequency_neg_spacing m k ε hε]

/-- The magnitude of the punctured frequency is phase divided by the magnitude
of the spacing.  This is the sign-free quantity relevant before selecting the
physical positive-spacing branch. -/
theorem abs_principalFrequency (m k ε : ℝ) (hε : ε ≠ 0) :
    |principalFrequency m k ε hε| = principalPhase m k ε / |ε| := by
  rw [principalFrequency, abs_div, abs_of_nonneg (principalPhase_nonneg m k ε)]

end KomorebiPhysics.Relativistic1DSpacingParity
