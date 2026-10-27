module

public import KomorebiPhysics.Relativistic1DShellAsymptotics

/-!
Algebraic coefficient matching for the 1D relativistic small-spacing expansion.
This isolates the nondegenerate division by continuum energy from the analytic
existence of a frequency expansion.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic1DAsymptoticAlgebra

open KomorebiPhysics.Relativistic1DShellAsymptotics

/-- The source's second-order frequency correction. -/
def correction (m k : ℝ) : ℝ := -(m^2 * k^2) / (6 * energy m k)

/-- A formal second-order frequency approximant. -/
def frequencyPoly2 (m k ε : ℝ) : ℝ := energy m k + correction m k * ε^2

/-- Continuum energy is nonnegative. -/
theorem energy_nonneg (m k : ℝ) : 0 ≤ energy m k := Real.sqrt_nonneg _

/-- Exact continuum mass-shell square. -/
theorem energy_sq (m k : ℝ) : energy m k ^ 2 = m^2 + k^2 := by
  rw [energy, Real.sq_sqrt (by positivity : 0 ≤ m^2 + k^2)]

/-- Zero continuum energy is exactly the doubly-degenerate point. -/
theorem energy_eq_zero_iff (m k : ℝ) : energy m k = 0 ↔ m = 0 ∧ k = 0 := by
  constructor
  · intro h
    have hsqrt : Real.sqrt (m^2 + k^2) = 0 := by simpa [energy] using h
    have hsum : m^2 + k^2 ≤ 0 := Real.sqrt_eq_zero'.mp hsqrt
    have hm : m^2 = 0 := by nlinarith [sq_nonneg k, sq_nonneg m]
    have hk : k^2 = 0 := by nlinarith [sq_nonneg k, sq_nonneg m]
    exact ⟨sq_eq_zero_iff.mp hm, sq_eq_zero_iff.mp hk⟩
  · rintro ⟨rfl, rfl⟩
    simp [energy]

/-- Nondegenerate mass or momentum gives positive continuum energy. -/
theorem energy_pos_of_nontrivial {m k : ℝ} (h : m ≠ 0 ∨ k ≠ 0) : 0 < energy m k := by
  exact lt_of_le_of_ne (energy_nonneg m k) (Ne.symm (mt (energy_eq_zero_iff m k).mp (by
    intro hmk
    exact h.elim (fun hm => hm hmk.1) (fun hk => hk hmk.2))))

/-- The correction is undefined only mathematically at zero energy; in Lean the formula is total,
but away from zero the intended denominator is certified. -/
theorem correction_formula (m k : ℝ) :
    correction m k = -(m^2 * k^2) / (6 * energy m k) := rfl

/-- The correction is even under mass reversal. -/
theorem correction_neg_mass (m k : ℝ) : correction (-m) k = correction m k := by
  simp [correction, energy]

/-- The correction is even under momentum reversal. -/
theorem correction_neg_momentum (m k : ℝ) : correction m (-k) = correction m k := by
  simp [correction, energy]

/-- Zero mass gives zero finite-spacing correction whenever the formula is evaluated. -/
theorem correction_zero_mass (k : ℝ) : correction 0 k = 0 := by simp [correction]

/-- Zero momentum gives zero finite-spacing correction. -/
theorem correction_zero_momentum (m : ℝ) : correction m 0 = 0 := by simp [correction]

/-- For nonzero continuum energy the correction is nonpositive. -/
theorem correction_nonpos {m k : ℝ} (hE : energy m k ≠ 0) : correction m k ≤ 0 := by
  rw [correction]
  have hEp : 0 < energy m k := lt_of_le_of_ne (energy_nonneg m k) (Ne.symm hE)
  exact div_nonpos_of_nonpos_of_nonneg
    (neg_nonpos.mpr (mul_nonneg (sq_nonneg m) (sq_nonneg k)))
    (mul_nonneg (by norm_num) hEp.le)

/-- Matching the quartic cosine coefficient forces the source correction. -/
theorem coefficient_match_unique {m k a : ℝ} (hE : energy m k ≠ 0)
    (hmatch : energy m k ^ 4 / 24 - energy m k * a =
      energy m k ^ 4 / 24 + m^2 * k^2 / 6) :
    a = correction m k := by
  rw [correction]
  have h6E : (6 : ℝ) * energy m k ≠ 0 := mul_ne_zero (by norm_num) hE
  field_simp [h6E]
  nlinarith

/-- Conversely the source correction gives exactly the required coefficient match. -/
theorem correction_matches_quartic {m k : ℝ} (hE : energy m k ≠ 0) :
    energy m k ^ 4 / 24 - energy m k * correction m k =
      energy m k ^ 4 / 24 + m^2 * k^2 / 6 := by
  rw [correction]
  field_simp [hE]
  ring

/-- Exact square of the second-order frequency approximant. -/
theorem frequencyPoly2_sq (m k ε : ℝ) :
    frequencyPoly2 m k ε ^ 2 =
      energy m k ^ 2 + 2 * energy m k * correction m k * ε^2 +
        correction m k ^ 2 * ε^4 := by
  rw [frequencyPoly2]
  ring

/-- The source correction gives the squared-shell coefficient `-m²k²/3`. -/
theorem twice_energy_mul_correction {m k : ℝ} (hE : energy m k ≠ 0) :
    2 * energy m k * correction m k = -(m^2 * k^2) / 3 := by
  rw [correction]
  field_simp [hE]
  ring

/-- Exact polynomial form underlying equation (8.12). -/
theorem frequencyPoly2_sq_mass_shell {m k ε : ℝ} (hE : energy m k ≠ 0) :
    frequencyPoly2 m k ε ^ 2 - k^2 - m^2 =
      -(m^2 * k^2) / 3 * ε^2 + correction m k ^ 2 * ε^4 := by
  rw [frequencyPoly2_sq, energy_sq, twice_energy_mul_correction hE]
  ring

/-- The quartic shell coefficient splits into the continuum term and the correction-driving term. -/
theorem shell_quartic_split (m k : ℝ) :
    shellQuarticCoeff m k = energy m k ^ 4 / 24 + m^2*k^2/6 := by
  exact shellQuarticCoeff_eq_source m k

/-- The second-order approximant is exactly continuum energy at zero spacing. -/
theorem frequencyPoly2_zero_spacing (m k : ℝ) : frequencyPoly2 m k 0 = energy m k := by
  simp [frequencyPoly2]

/-- The formal correction is genuinely nonzero when both parameters are nonzero. -/
theorem correction_ne_zero {m k : ℝ} (hm : m ≠ 0) (hk : k ≠ 0) : correction m k ≠ 0 := by
  have hE : energy m k ≠ 0 := by
    intro hzero
    exact hm ((energy_eq_zero_iff m k).mp hzero).1
  rw [correction]
  exact div_ne_zero (neg_ne_zero.mpr (mul_ne_zero (pow_ne_zero 2 hm) (pow_ne_zero 2 hk)))
    (mul_ne_zero (by norm_num) hE)

end KomorebiPhysics.Relativistic1DAsymptoticAlgebra
