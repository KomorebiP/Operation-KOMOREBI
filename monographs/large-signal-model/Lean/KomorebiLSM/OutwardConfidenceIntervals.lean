import KomorebiLSM.RationalConfidenceArithmetic

/-! Exact endpoint rounding and intersection with the declared true prior. -/
set_option autoImplicit false
namespace Komorebi.LSM.OutwardConfidenceIntervals

noncomputable def roundDown (denominator : ℕ) (x : ℝ) : ℚ :=
  (⌊(denominator : ℝ)*x⌋ : ℚ)/(denominator : ℚ)
noncomputable def roundUp (denominator : ℕ) (x : ℝ) : ℚ :=
  (⌈(denominator : ℝ)*x⌉ : ℚ)/(denominator : ℚ)

theorem roundDown_le (denominator : ℕ) (hd : 0<denominator) (x : ℝ) :
    (roundDown denominator x : ℝ)≤x := by
  have hdr : (0 : ℝ)<denominator := by exact_mod_cast hd
  unfold roundDown
  push_cast
  apply (div_le_iff₀ hdr).mpr
  simpa only [mul_comm] using Int.floor_le ((denominator : ℝ)*x)

theorem le_roundUp (denominator : ℕ) (hd : 0<denominator) (x : ℝ) :
    x≤(roundUp denominator x : ℝ) := by
  have hdr : (0 : ℝ)<denominator := by exact_mod_cast hd
  unfold roundUp
  push_cast
  apply (le_div_iff₀ hdr).mpr
  simpa only [mul_comm] using Int.le_ceil ((denominator : ℝ)*x)

noncomputable def lowerEndpoint (denominator : ℕ) (center : ℝ) (radius : ℚ) : ℚ :=
  max (-1) (roundDown denominator (center-radius))
noncomputable def upperEndpoint (denominator : ℕ) (center : ℝ) (radius : ℚ) : ℚ :=
  min 1 (roundUp denominator (center+radius))

/-- Enlarging by an upper radius and rounding outward preserves every true
parameter that also obeys the prior interval. -/
theorem contains_true (denominator : ℕ) (hd : 0<denominator) (center theta bound : ℝ)
    (radius : ℚ) (herror : |center-theta|≤bound) (hbound : bound≤(radius : ℝ))
    (hprior : |theta|≤1) :
    theta∈Set.Icc (lowerEndpoint denominator center radius : ℝ)
      (upperEndpoint denominator center radius : ℝ) := by
  have he := (abs_le.mp (herror.trans hbound))
  have hp := abs_le.mp hprior
  have hl := roundDown_le denominator hd (center-radius)
  have hu := le_roundUp denominator hd (center+radius)
  constructor
  · unfold lowerEndpoint
    push_cast
    exact max_le hp.1 (by linarith)
  · unfold upperEndpoint
    push_cast
    exact le_min hp.2 (by linarith)

/-- Intersecting with a prior known to contain the truth preserves coverage,
including after arbitrary selection from a simultaneous event. -/
theorem selected_contains {Ω : Type*} (denominator : ℕ) (hd : 0<denominator)
    (G : Set Ω) (center : ℕ → Ω → ℝ) (radius : ℕ → Ω → ℚ) (theta : ℝ)
    (hall : ∀ ω∈G,∀ n,|center n ω-theta|≤(radius n ω : ℝ)) (hprior : |theta|≤1)
    (time : Ω → ℕ) (ω : Ω) (hω : ω∈G) :
    theta∈Set.Icc (lowerEndpoint denominator (center (time ω) ω) (radius (time ω) ω) : ℝ)
      (upperEndpoint denominator (center (time ω) ω) (radius (time ω) ω) : ℝ) :=
  contains_true denominator hd _ theta _ _ (hall ω hω (time ω)) le_rfl hprior

end Komorebi.LSM.OutwardConfidenceIntervals
