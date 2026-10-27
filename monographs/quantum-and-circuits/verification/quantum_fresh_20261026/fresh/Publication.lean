import Conventions

set_option autoImplicit false
set_option maxHeartbeats 2000000
open scoped Matrix BigOperators
namespace Komorebi.QuantumArithmetic

/-- The exact root sum and the rational signal are the same indexed vector. -/
theorem exact_phase_signal_lookup (i : Index) :
    ramanujanC12 i.val = cRat (ramanujan12.getD i.val 0) := by
  decide +kernel +revert

/-- The essay's phase sum is the actual complex Ramanujan signal, not only a coordinate table. -/
theorem complex_ramanujan_signal (i : Index) :
    ((unitResidues12.map (fun a =>
      Complex.exp (((Real.pi / 6 : ℝ) : ℂ) * Complex.I) ^ (a * i.val))).sum) =
      (ramanujan12.getD i.val 0 : ℂ) := by
  have h := congrArg interpret (exact_phase_signal_lookup i)
  simpa [ramanujanC12, List.map_map, Function.comp_def, root_is_exponential] using h

/-- The replacement state really takes the absolute value of the real signal. -/
theorem absolute_signal_lookup (i : Index) :
    absRamanujan12.getD i.val 0 = |ramanujan12.getD i.val 0| := by
  decide +kernel +revert

/-- Exact orthogonality behind the numerical energy identity in the example. -/
theorem retained_discarded_orthogonal : dot ramanujan12 noise12 = 0 := by
  decide +kernel +revert

theorem signal_decomposition : vecAdd ramanujan12 noise12 = testSignal12 := by
  decide +kernel +revert

/-- Every signal is reconstructible from the retained and discarded components together. -/
theorem projector_residual_reconstructs (v : Index → ℂ) :
    P.mulVec v + (1 - P).mulVec v = v := by
  rw [Matrix.sub_mulVec, Matrix.one_mulVec]
  exact add_sub_cancel _ _

/-- No state reconstruction function can invert the initial probability histogram on both states. -/
theorem no_reconstruction_from_initial_probabilities :
    ¬ ∃ R : (Index → ℝ) → (Index → ℂ),
      R (fun i => Complex.normSq (psi i)) = psi ∧
      R (fun i => Complex.normSq (chi i)) = chi := by
  rintro ⟨R, hpsi, hchi⟩
  have heq : (fun i => Complex.normSq (psi i)) =
      (fun i => Complex.normSq (chi i)) := funext same_initial_probabilities
  have hstate : psi = chi := by rw [← hpsi, ← hchi, heq]
  have h := signed_state_recovers_arithmetic
  rw [hstate, unsigned_state_erases_arithmetic] at h
  norm_num at h

/-- Exact probabilities in the recovered basis, connected to the normalized state. -/
theorem recovered_probability_at (i : Index) :
    Complex.normSq (Fᴴ.mulVec psi i) =
      if Nat.gcd i.val 12 = 1 then (1/4 : ℝ) else 0 := by
  rw [state_recovery, unitState_entry_formula]
  by_cases h : Nat.gcd i.val 12 = 1 <;> norm_num [h, Complex.normSq_apply]

/-- The operator is not injective. Its nonzero normalized kernel state is explicit. -/
theorem projector_not_injective : ¬ Function.Injective P.mulVec := by
  intro h
  have hz : chi = 0 := h (by simp [projector_kills_chi])
  have hp := chi_normalized
  rw [hz] at hp
  norm_num [totalProbability] at hp

/-- Publication theorem gathering the complex identities stated in the worked example. -/
theorem publication_bridge :
    Fᴴ * F = 1 ∧ F * Fᴴ = 1 ∧ F * D * Fᴴ = P ∧
    P * P = P ∧ Pᴴ = P ∧ F.mulVec unitState = psi ∧
    Fᴴ.mulVec psi = unitState ∧ totalProbability psi = 1 ∧
    totalProbability chi = 1 ∧
    (∀ i, Complex.normSq (psi i) = Complex.normSq (chi i)) ∧
    (∑ i, star (psi i) * chi i) = 0 ∧
    coprimeProbability (Fᴴ.mulVec psi) = 1 ∧
    coprimeProbability (Fᴴ.mulVec chi) = 0 := by
  exact ⟨fourier_unitary_left, fourier_unitary_right, projector_transport,
    projector_idempotent_complex, projector_selfAdjoint_complex, state_preparation,
    state_recovery, psi_normalized, chi_normalized, same_initial_probabilities,
    states_orthogonal, signed_state_recovers_arithmetic, unsigned_state_erases_arithmetic⟩

end Komorebi.QuantumArithmetic
