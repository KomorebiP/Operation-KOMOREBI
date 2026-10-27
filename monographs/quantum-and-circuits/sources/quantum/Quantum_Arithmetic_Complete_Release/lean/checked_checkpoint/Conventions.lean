import SemanticBridge
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Positivity

set_option autoImplicit false
set_option maxHeartbeats 2000000
open scoped Matrix BigOperators
namespace Komorebi.QuantumArithmetic

/-- The coordinate root is exactly the usual exponential twelfth root. -/
theorem root_is_exponential :
    interpret zeta12 = Complex.exp (((Real.pi / 6 : ℝ) : ℂ) * Complex.I) := by
  rw [Complex.exp_mul_I]
  rw [← Complex.ofReal_cos, ← Complex.ofReal_sin, Real.cos_pi_div_six, Real.sin_pi_div_six]
  apply Complex.ext <;> simp [interpret, zeta12]
  ring

theorem root_power_twelve : interpret zeta12 ^ 12 = 1 := by
  simpa using congrArg interpret zeta12_order_certificate

theorem rootPower_interpret (n : Nat) :
    interpret (rootPower n) = interpret zeta12 ^ n := by
  simp only [rootPower, interpret_pow]
  exact (pow_eq_pow_mod n root_power_twelve).symm

theorem sqrt_twelve : Real.sqrt 12 = 2 * Real.sqrt 3 := by
  calc
    Real.sqrt 12 = Real.sqrt (4 * 3) := by norm_num
    _ = Real.sqrt 4 * Real.sqrt 3 := Real.sqrt_mul (by norm_num) _
    _ = 2 * Real.sqrt 3 := by
      rw [show Real.sqrt 4 = 2 from by
        rw [show (4 : ℝ) = 2^2 by norm_num, Real.sqrt_sq (by norm_num)]]

theorem sqrt_fortyeight : Real.sqrt 48 = 4 * Real.sqrt 3 := by
  calc
    Real.sqrt 48 = Real.sqrt (16 * 3) := by norm_num
    _ = Real.sqrt 16 * Real.sqrt 3 := Real.sqrt_mul (by norm_num) _
    _ = 4 * Real.sqrt 3 := by
      rw [show Real.sqrt 16 = 4 from by
        rw [show (16 : ℝ) = 4^2 by norm_num, Real.sqrt_sq (by norm_num)]]

theorem fourierScale_interpret :
    interpret fourierScale = ((1 / Real.sqrt 12 : ℝ) : ℂ) := by
  apply Complex.ext <;> simp [interpret, fourierScale, sqrt_twelve]
  have h : Real.sqrt 3 ≠ 0 := by positivity
  field_simp
  nlinarith [Real.sq_sqrt (show (0 : ℝ) ≤ 3 by norm_num)]

theorem stateScale_interpret :
    interpret stateScale = ((1 / Real.sqrt 48 : ℝ) : ℂ) := by
  apply Complex.ext <;> simp [interpret, stateScale, sqrt_fortyeight]
  have h : Real.sqrt 3 ≠ 0 := by positivity
  field_simp
  nlinarith [Real.sq_sqrt (show (0 : ℝ) ≤ 3 by norm_num)]

/-- The matrix checked in the certificate is the standard positive sign Fourier matrix. -/
theorem fourier_entry_formula (i j : Index) :
    F i j = ((1 / Real.sqrt 12 : ℝ) : ℂ) *
      Complex.exp (2 * (Real.pi : ℂ) * Complex.I * (i.val : ℂ) * (j.val : ℂ) / 12) := by
  simp only [F, complexMatrix, exactFourier, interpret_mul, fourierScale_interpret,
    rootPower_interpret, root_is_exponential]
  rw [← Complex.exp_nat_mul]
  congr 2
  push_cast
  ring

theorem psi_entry_formula (i : Index) :
    psi i = ((1 / Real.sqrt 48 : ℝ) : ℂ) * (ramanujan12.getD i.val 0 : ℂ) := by
  simp [psi, complexVector, exactPsi, stateScale_interpret]

theorem chi_entry_formula (i : Index) :
    chi i = ((1 / Real.sqrt 48 : ℝ) : ℂ) * (absRamanujan12.getD i.val 0 : ℂ) := by
  simp [chi, complexVector, exactChi, stateScale_interpret]

theorem unitState_entry_formula (i : Index) :
    unitState i = if Nat.gcd i.val 12 = 1 then (1/2 : ℂ) else 0 := by
  by_cases h : Nat.gcd i.val 12 = 1 <;>
    simp [unitState, complexVector, exactUnitState, h]

theorem projector_entry_formula (i j : Index) :
    P i j = (ramanujan12.getD ((i.val + 12 - j.val) % 12) 0 : ℂ) / 12 := by
  simp [P, complexMatrix, exactProjector]

theorem selector_idempotent : D * D = D := by
  unfold D
  rw [Matrix.diagonal_mul_diagonal]
  congr 1
  funext i
  by_cases h : Nat.gcd i.val 12 = 1 <;> simp [h]

theorem selector_selfAdjoint : Dᴴ = D := by
  ext i j
  by_cases h : i = j
  · subst j
    simp [D, Matrix.conjTranspose_apply, apply_ite star]
  · simp [D, Matrix.conjTranspose_apply, h, Ne.symm h]

theorem projector_idempotent_complex : P * P = P := by
  rw [← projector_transport]
  calc
    (F * D * Fᴴ) * (F * D * Fᴴ) = F * D * (Fᴴ * F) * D * Fᴴ := by
      simp only [Matrix.mul_assoc]
    _ = F * D * Fᴴ := by rw [fourier_unitary_left, Matrix.mul_one, Matrix.mul_assoc F D D,
      selector_idempotent]

theorem projector_selfAdjoint_complex : Pᴴ = P := by
  rw [← projector_transport]
  simp [Matrix.conjTranspose_mul, selector_selfAdjoint, Matrix.mul_assoc]

/-- Projection alone loses information: two distinct normalized states are distinguished exactly. -/
theorem complete_phase_separation :
    totalProbability psi = 1 ∧ totalProbability chi = 1 ∧
    (∀ i, Complex.normSq (psi i) = Complex.normSq (chi i)) ∧
    (∑ i, star (psi i) * chi i) = 0 ∧
    coprimeProbability (Fᴴ.mulVec psi) = 1 ∧
    coprimeProbability (Fᴴ.mulVec chi) = 0 := by
  exact ⟨psi_normalized, chi_normalized, same_initial_probabilities, states_orthogonal,
    signed_state_recovers_arithmetic, unsigned_state_erases_arithmetic⟩

end Komorebi.QuantumArithmetic
