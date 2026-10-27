module

public import KomorebiPhysics.Relativistic3DGroupVelocity

/-!
Fixed-radius axis-versus-diagonal anisotropy for the exact three-dimensional
principal frequency.  This closes equations (8.37)--(8.41) after the checked
frequency expansion, while retaining the positive-spacing and nonzero-energy
hypotheses of the branch inversion.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic3DAnisotropy

open Filter Asymptotics
open scoped Topology
open KomorebiPhysics.Relativistic3DShellAsymptotics
open KomorebiPhysics.Relativistic3DContinuumLimit

/-- Common Cartesian coordinate of the fixed-radius body diagonal. -/
def diagCoord (κ : ℝ) : ℝ := κ / Real.sqrt 3

/-- Common continuum energy of the axis and body-diagonal momenta. -/
def fixedRadiusEnergy (m κ : ℝ) : ℝ := Real.sqrt (m^2 + κ^2)

/-- Exact axis branch at radius `κ`. -/
def axisFrequency3 (m κ ε : ℝ) : ℝ := positiveFrequency3 m κ 0 0 ε

/-- Exact body-diagonal branch at radius `κ`. -/
def diagonalFrequency3 (m κ ε : ℝ) : ℝ :=
  positiveFrequency3 m (diagCoord κ) (diagCoord κ) (diagCoord κ) ε

/-- `sqrt 3` is nonzero. -/
theorem sqrt_three_ne_zero : Real.sqrt (3 : ℝ) ≠ 0 := by positivity

/-- The diagonal coordinate has square `κ²/3`. -/
theorem diagCoord_sq (κ : ℝ) : diagCoord κ ^ 2 = κ^2 / 3 := by
  have hs : Real.sqrt (3 : ℝ) ^ 2 = 3 := by
    rw [Real.sq_sqrt]
    norm_num
  rw [diagCoord]
  field_simp [sqrt_three_ne_zero]
  nlinarith

/-- The three equal diagonal coordinates have total squared radius `κ²`. -/
theorem three_mul_diagCoord_sq (κ : ℝ) :
    3 * diagCoord κ ^ 2 = κ^2 := by
  rw [diagCoord_sq]
  ring

/-- Equation (8.37): the axis momentum has radius squared `κ²`. -/
theorem axis_radius_sq (κ : ℝ) : κ^2 + 0^2 + 0^2 = κ^2 := by ring

/-- Equation (8.38): the body-diagonal momentum has radius squared `κ²`. -/
theorem diagonal_radius_sq (κ : ℝ) :
    diagCoord κ ^ 2 + diagCoord κ ^ 2 + diagCoord κ ^ 2 = κ^2 := by
  nlinarith [three_mul_diagCoord_sq κ]

/-- The axis branch has the fixed-radius continuum energy. -/
theorem energy3_axis (m κ : ℝ) :
    energy3 m κ 0 0 = fixedRadiusEnergy m κ := by
  simp [energy3, fixedRadiusEnergy]

/-- The body diagonal has the same fixed-radius continuum energy. -/
theorem energy3_diagonal (m κ : ℝ) :
    energy3 m (diagCoord κ) (diagCoord κ) (diagCoord κ) =
      fixedRadiusEnergy m κ := by
  rw [energy3, fixedRadiusEnergy]
  congr 1
  nlinarith [diagonal_radius_sq κ]

/-- Axis and diagonal continuum energies coincide exactly at fixed radius. -/
theorem energy3_axis_eq_diagonal (m κ : ℝ) :
    energy3 m κ 0 0 =
      energy3 m (diagCoord κ) (diagCoord κ) (diagCoord κ) := by
  rw [energy3_axis, energy3_diagonal]

/-- Equation (8.40): the axis anisotropy polynomial. -/
theorem anisotropyQ_axis (m κ : ℝ) :
    anisotropyQ m κ 0 0 = m^2 * κ^2 := by
  simp [anisotropyQ]

/-- Equation (8.41): the body-diagonal anisotropy polynomial. -/
theorem anisotropyQ_diagonal (m κ : ℝ) :
    anisotropyQ m (diagCoord κ) (diagCoord κ) (diagCoord κ) =
      m^2 * κ^2 + κ^4 / 3 := by
  rw [anisotropyQ]
  rw [diagCoord_sq]
  ring

/-- The diagonal anisotropy exceeds the axis anisotropy by `κ⁴/3`. -/
theorem anisotropyQ_diagonal_sub_axis (m κ : ℝ) :
    anisotropyQ m (diagCoord κ) (diagCoord κ) (diagCoord κ) -
      anisotropyQ m κ 0 0 = κ^4 / 3 := by
  rw [anisotropyQ_axis, anisotropyQ_diagonal]
  ring

/-- Difference of the checked quadratic frequency coefficients. -/
theorem correction3_axis_sub_diagonal {m κ : ℝ}
    (hE : fixedRadiusEnergy m κ ≠ 0) :
    correction3 m κ 0 0 -
      correction3 m (diagCoord κ) (diagCoord κ) (diagCoord κ) =
        κ^4 / (18 * fixedRadiusEnergy m κ) := by
  rw [correction3, correction3]
  rw [anisotropyQ_axis, anisotropyQ_diagonal]
  rw [energy3_axis, energy3_diagonal]
  field_simp [hE]
  ring

/-- Equation (8.39): fixed-radius axis frequency exceeds the diagonal branch
by `κ⁴ Δ²/(18E)` up to a genuine fourth-order remainder. -/
theorem axis_sub_diagonal_frequency_expansion_isBigO {m κ : ℝ}
    (hE : fixedRadiusEnergy m κ ≠ 0) :
    (fun ε => axisFrequency3 m κ ε - diagonalFrequency3 m κ ε -
      (κ^4 / (18 * fixedRadiusEnergy m κ)) * ε^2)
        =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  have hEa : energy3 m κ 0 0 ≠ 0 := by
    simpa [energy3_axis] using hE
  have hEd :
      energy3 m (diagCoord κ) (diagCoord κ) (diagCoord κ) ≠ 0 := by
    simpa [energy3_diagonal] using hE
  have ha := positiveFrequency3_expansion_isBigO hEa
  have hd := positiveFrequency3_expansion_isBigO hEd
  have hsub := ha.sub hd
  exact hsub.congr_left (by
    intro ε
    dsimp [axisFrequency3, diagonalFrequency3, frequencyPoly2_3]
    rw [energy3_axis, energy3_diagonal]
    calc
      positiveFrequency3 m κ 0 0 ε -
          (fixedRadiusEnergy m κ + correction3 m κ 0 0 * ε ^ 2) -
          (positiveFrequency3 m (diagCoord κ) (diagCoord κ) (diagCoord κ) ε -
            (fixedRadiusEnergy m κ +
              correction3 m (diagCoord κ) (diagCoord κ) (diagCoord κ) * ε ^ 2)) =
          positiveFrequency3 m κ 0 0 ε -
            positiveFrequency3 m (diagCoord κ) (diagCoord κ) (diagCoord κ) ε -
            (correction3 m κ 0 0 -
              correction3 m (diagCoord κ) (diagCoord κ) (diagCoord κ)) * ε ^ 2 := by
                ring
      _ = positiveFrequency3 m κ 0 0 ε -
            positiveFrequency3 m (diagCoord κ) (diagCoord κ) (diagCoord κ) ε -
            (κ ^ 4 / (18 * fixedRadiusEnergy m κ)) * ε ^ 2 := by
              rw [correction3_axis_sub_diagonal hE])

/-- The anisotropy coefficient is strictly positive away from zero radius. -/
theorem axis_sub_diagonal_coefficient_pos {m κ : ℝ}
    (hκ : κ ≠ 0) (hE : fixedRadiusEnergy m κ ≠ 0) :
    0 < κ^4 / (18 * fixedRadiusEnergy m κ) := by
  have hEp : 0 < fixedRadiusEnergy m κ := by
    exact lt_of_le_of_ne (Real.sqrt_nonneg _) (Ne.symm hE)
  positivity

/-- Exact unit-radius massless coefficient witness. -/
theorem massless_unit_axis_sub_diagonal_coefficient :
    (1 : ℝ)^4 / (18 * fixedRadiusEnergy 0 1) = 1 / 18 := by
  norm_num [fixedRadiusEnergy]

end KomorebiPhysics.Relativistic3DAnisotropy
