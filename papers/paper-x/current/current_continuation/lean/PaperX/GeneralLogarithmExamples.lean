import PaperX.GeneralReconstructionRecovery
import PaperX.ReconstructionBoundary

/-! Actual affine representations with arbitrarily long monodromy chains.
The quartic example lies outside the predecessor's cubic recovery class. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.GeneralLogarithmExamples
open PaperX.WeilData PaperX.WeilSpecialChain PaperX.SpecialMonodromy
open PaperX.AffineMonodromy PaperX.ReconstructionExamples
open PaperX.NilpotentExponential PaperX.MonodromyReconstruction
open PaperX.LogarithmicRecovery

def chainAction (n : ℕ) : Representation ℚ G (Fin n → ℚ) :=
  reconstruct (chain ℚ n) chosenCocycle

theorem chain_translation_action (n : ℕ) : (chain ℚ n).r u = 1 := by
  ext x j
  simp [chain, chainDatum, chainRep, diagonalF, norm, u, translation,
    SemidirectProduct.rightHom]

theorem chain_sample (n : ℕ) : chainAction n u = expN (chain ℚ n).N 1 := by
  apply LinearMap.ext
  intro x
  change expN (chain ℚ n).N (chosenCocycle.value u) ((chain ℚ n).r u x) = _
  rw [chain_translation_action]
  rfl

/-- This invokes the general extraction theorem for every chain length. -/
theorem recover_arbitrary_chain (n : ℕ) : recoverN 1 (chainAction n u) = (chain ℚ n).N := by
  rw [chain_sample]
  exact recoverN_expN (chain ℚ n).nilpotent (by norm_num)

theorem arbitrary_chain_fixed_vectors (n : ℕ) (x : Fin n → ℚ) :
    chainAction n u x = x ↔ (chain ℚ n).N x = 0 := by
  rw [chain_sample]
  exact expN_fixed_iff (chain ℚ n).nilpotent (by norm_num) x

theorem sixth_order_example :
    (chain ℚ 6).N ^ 5 ≠ 0 ∧ (chain ℚ 6).N ^ 6 = 0 ∧
      recoverN 1 (chainAction 6 u) = (chain ℚ 6).N :=
  ⟨shift_previous_power_nonzero 6 (by decide), shift_nilpotent 6,
    recover_arbitrary_chain 6⟩

/-- The former quartic counterexample is now recovered by the full logarithm. -/
theorem quartic_recovered_but_quadratic_fails :
    recoverN 1 (expN PaperX.ReconstructionBoundary.datum4.N 1) =
      PaperX.ReconstructionBoundary.datum4.N ∧
    PaperX.UnipotentLogarithm.log₂ (expN PaperX.ReconstructionBoundary.datum4.N 1) ≠
      PaperX.ReconstructionBoundary.datum4.N := by
  exact ⟨recoverN_expN PaperX.ReconstructionBoundary.datum4.nilpotent (by norm_num),
    PaperX.ReconstructionBoundary.quadratic_log_fails_beyond_cube⟩

theorem recover_arbitrary_chain_parameter (n : ℕ) (s : ℚ) (hs : s ≠ 0) :
    recoverN s (expN (chain ℚ n).N s) = (chain ℚ n).N :=
  recoverN_expN (chain ℚ n).nilpotent hs

/-- The parameter restriction remains essential even with the complete logarithm. -/
theorem general_zero_parameter_recovery_fails :
    recoverN 0 (expN datum3.N 0) ≠ datum3.N := by
  simpa [recoverN] using PaperX.ReconstructionBoundary.monodromy_nonzero.symm

/-- Any reconstructed-action intertwiner between two arbitrary chain lengths
recovers both the original affine action and monodromy. -/
theorem arbitrary_chain_intertwiner (n m : ℕ) (f : (Fin n → ℚ) →ₗ[ℚ] (Fin m → ℚ)) :
    (∀ g x, f (chainAction n g x) = chainAction m g (f x)) ↔
      (∀ g x, f ((chain ℚ n).r g x) = (chain ℚ m).r g (f x)) ∧
        (chain ℚ m).N ∘ₗ f = f ∘ₗ (chain ℚ n).N := by
  exact PaperX.GeneralReconstructionRecovery.reconstruct_intertwiner_iff
    chosenCocycle u (chain_translation_action n) (chain_translation_action m)
    (by norm_num [chosenCocycle, translation_value.1]) f

end PaperX.GeneralLogarithmExamples
