import PaperX.GeneralLogarithmExamples

/-! The original-action sample condition remains essential. An exponential
factor can be absorbed into the supplied original group action, giving the
same reconstructed representation with different monodromy data. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.GeneralRecoveryBoundary
open PaperX.WeilData PaperX.MonodromyReconstruction

variable {K G : Type*} [Field K] [CharZero K] [Group G] {ν : G →* Kˣ}
variable {V : Type*} [AddCommGroup V] [Module K V]

/-- Absorb the whole reconstructed action into r and set monodromy to zero. -/
def absorbed (D : Datum ν V) (t : TwistedCocycle ν) : Datum ν V where
  r := reconstruct D t
  N := 0
  nilpotent := ⟨1, by simp⟩
  relation g x := by simp

theorem absorbed_reconstruct (D : Datum ν V) (t : TwistedCocycle ν) :
    reconstruct (absorbed D t) t = reconstruct D t := by
  ext g x
  simp [absorbed, reconstruct_apply, unipotent, PaperX.NilpotentExponential.expN]

theorem absorbed_monodromy (D : Datum ν V) (t : TwistedCocycle ν) :
    (absorbed D t).N = 0 := rfl

open PaperX.AffineMonodromy PaperX.ReconstructionExamples
open PaperX.GeneralLogarithmExamples PaperX.LogarithmicRecovery
open PaperX.SpecialMonodromy

theorem long_chain_monodromy_nonzero : (chain ℚ 6).N ≠ 0 := by
  intro h
  have hn := (sixth_order_example).1
  simp [h] at hn

/-- Equal reconstructed representations and a nonzero cocycle sample do not
by themselves determine the original monodromy datum. -/
theorem identical_reconstruction_different_monodromy :
    reconstruct (absorbed (chain ℚ 6) chosenCocycle) chosenCocycle = chainAction 6 ∧
      (absorbed (chain ℚ 6) chosenCocycle).N ≠ (chain ℚ 6).N ∧
      chosenCocycle.value u ≠ 0 := by
  exact ⟨absorbed_reconstruct _ _, long_chain_monodromy_nonzero.symm,
    by norm_num [chosenCocycle, translation_value.1]⟩

/-- The absorbed datum fails exactly the original-action hypothesis used in
the general extraction theorem. -/
theorem absorbed_original_sample_nontrivial :
    (absorbed (chain ℚ 6) chosenCocycle).r u ≠ 1 := by
  intro h
  have hs : chainAction 6 u = 1 := h
  have hr := recover_arbitrary_chain 6
  rw [hs] at hr
  have hz : (chain ℚ 6).N = 0 := by
    simpa [recoverN, PaperX.FiniteLogarithm.log_one] using hr.symm
  exact long_chain_monodromy_nonzero hz

/-- The complete logarithm still cannot recover an arbitrary supplied N
unless the known original action is trivial at the sample. -/
theorem recovery_without_original_sample_fails :
    recoverN 1 (reconstruct (absorbed (chain ℚ 6) chosenCocycle) chosenCocycle u) ≠
      (absorbed (chain ℚ 6) chosenCocycle).N := by
  intro hbad
  have he := congrArg (fun ρ : Representation ℚ (Affine ℚ) (Fin 6 → ℚ) =>
    recoverN 1 (ρ u)) (absorbed_reconstruct (chain ℚ 6) chosenCocycle)
  have hrec : recoverN 1
      (reconstruct (absorbed (chain ℚ 6) chosenCocycle) chosenCocycle u) =
        (chain ℚ 6).N := he.trans (recover_arbitrary_chain 6)
  exact long_chain_monodromy_nonzero (hrec.symm.trans hbad)


end PaperX.GeneralRecoveryBoundary
